from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal, InvalidOperation
import math
import json

from django.http import HttpResponseNotAllowed, JsonResponse
from django.contrib.auth.forms import AuthenticationForm

from .models import Portfolio, UserProfile, Position, TradeHistory
from .forms import CustomUserCreationForm
from .tasks import perform_full_analysis 


def home(request):
    username = request.user.username if request.user.is_authenticated else None
    context = {'username': username}
    return render(request, 'trading_app/home.html', context)

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            balance = form.cleaned_data.get('initial_balance')
            api_key = form.cleaned_data.get('gemini_api_key')
            Portfolio.objects.create(user=user, balance=balance)
            UserProfile.objects.create(user=user, gemini_api_key=api_key)
            login(request, user)
            return redirect('trading_app:dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'trading_app/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('trading_app:dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'trading_app/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('trading_app:home')

@login_required
def dashboard_view(request):
    portfolio, _ = Portfolio.objects.get_or_create(user=request.user)
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    
    context = {
        'portfolio': portfolio,
        'positions': portfolio.positions.all(),
        'trade_history': portfolio.trade_history.order_by('-timestamp')[:5]
    }
    return render(request, 'trading_app/dashboard.html', context)

@login_required
def start_analysis(request):
    if request.method == 'POST':
        user = request.user
        analysis_result = perform_full_analysis(user.id)
        return JsonResponse(analysis_result)
        
    return HttpResponseNotAllowed(['POST'])

@login_required
def execute_trade_view(request):
    if request.method == 'POST':
        portfolio = Portfolio.objects.get(user=request.user)
        action = request.POST.get('action'); ticker = request.POST.get('ticker')
        quantity = int(request.POST.get('quantity')); price_str = request.POST.get('price', '0').replace(',', '.')
        try:
            price = Decimal(price_str)
        except InvalidOperation:
            messages.error(request, "O formato do preço recebido é inválido.")
            return redirect('trading_app:dashboard')

        if action == 'BUY':
            trade_value = price * quantity
            if portfolio.balance >= trade_value:
                portfolio.balance -= trade_value
                Position.objects.create(portfolio=portfolio, ticker=ticker, quantity=quantity, buy_price=price)
                TradeHistory.objects.create(portfolio=portfolio, ticker=ticker, side='BUY', quantity=quantity, price=price)
                portfolio.save()
                messages.success(request, f"Compra de {quantity}x {ticker} executada com sucesso!")
            else:
                messages.error(request, "Saldo insuficiente para executar a compra.")
        
        elif action == 'SELL':
            position_to_sell = Position.objects.filter(portfolio=portfolio, ticker=ticker).first()
            if position_to_sell:
                trade_value = price * quantity
                portfolio.balance += trade_value
                TradeHistory.objects.create(portfolio=portfolio, ticker=ticker, side='SELL', quantity=quantity, price=price)
                position_to_sell.delete()
                portfolio.save()
                messages.success(request, f"Venda de {quantity}x {ticker} executada com sucesso!")
            else:
                messages.error(request, "Posição não encontrada para venda.")
        return redirect('trading_app:dashboard')
    return HttpResponseNotAllowed(['POST'])

@login_required
def update_balance_view(request):
    if request.method == 'POST':
        portfolio = Portfolio.objects.get(user=request.user)
        amount = Decimal(request.POST.get('amount', '0'))
        if portfolio.balance + amount >= 0:
            portfolio.balance += amount
            portfolio.save()
            messages.success(request, f"Saldo ajustado em R$ {amount:,.2f}.")
        else:
            messages.error(request, "Não é possível deixar o saldo negativo.")
        return redirect('trading_app:dashboard')
    return HttpResponseNotAllowed(['POST'])

@login_required
def report_view(request):
    portfolio = Portfolio.objects.get(user=request.user)
    trade_history = portfolio.trade_history.order_by('timestamp').all()
    
    pnl = Decimal(0)
    wins = 0
    total_trades = 0
    
    for trade in trade_history:
        if trade.side == 'SELL':
            buy_trade = portfolio.trade_history.filter(ticker=trade.ticker, side='BUY', timestamp__lt=trade.timestamp).last()
            if buy_trade:
                pnl += (trade.price - buy_trade.price) * trade.quantity
                if trade.price > buy_trade.price:
                    wins += 1
                total_trades += 1

    win_rate = (wins / total_trades * 100) if total_trades > 0 else 0

    balance_over_time = {'labels': [], 'data': []}
    if trade_history.exists():
        current_balance = portfolio.balance
        balance_points = []

        temp_balance = current_balance
        all_trades = list(reversed(trade_history))
        
        for i, trade in enumerate(all_trades):
            balance_points.append((trade.timestamp, float(temp_balance)))
            if trade.side == 'BUY':
                temp_balance += trade.price * Decimal(trade.quantity)
            else: # SELL
                temp_balance -= trade.price * Decimal(trade.quantity)
        
        initial_balance = temp_balance
        if trade_history:
             first_trade_time = trade_history.first().timestamp
             balance_points.append((first_trade_time, float(initial_balance)))


        balance_points.reverse()

        balance_over_time['labels'] = [p[0].strftime('%Y-%m-%d %H:%M') for p in balance_points]
        balance_over_time['data'] = [p[1] for p in balance_points]

    context = {
        'portfolio': portfolio,
        'trade_history': trade_history,
        'total_pl': pnl, 
        'win_rate': win_rate,
        'total_trades': total_trades,
        'chart_data': json.dumps(balance_over_time) 
    }
    return render(request, 'trading_app/report.html', context)

