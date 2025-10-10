# trading_app/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal, InvalidOperation
import json
from django.http import HttpResponseNotAllowed, JsonResponse
from django.contrib.auth.forms import AuthenticationForm
from django.utils import timezone
from .models import Portfolio, UserProfile, Position, TradeHistory
from .forms import CustomUserCreationForm
from . import tasks

# Import para tarefas em segundo plano
import django_rq 
from rq.job import Job

def home(request):
    if request.user.is_authenticated:
        return redirect('trading_app:dashboard')
    return render(request, 'trading_app/home.html')

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
    portfolio = Portfolio.objects.get(user=request.user)
    context = {
        'portfolio': portfolio,
        'positions': portfolio.positions.all(),
    }
    return render(request, 'trading_app/dashboard.html', context)

@login_required
def start_analysis_view(request):
    if request.method == 'POST':
        user_profile = UserProfile.objects.get(user=request.user)
        if not user_profile.gemini_api_key:
            return JsonResponse({'error': 'Você precisa salvar sua chave de API do Gemini primeiro.'}, status=400)

        queue = django_rq.get_queue('default')
        job = queue.enqueue(tasks.perform_full_analysis, request.user.id)
        return JsonResponse({'job_id': job.id})
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def check_analysis_result_view(request, job_id):
    queue = django_rq.get_queue('default')
    try:
        job = Job.fetch(job_id, connection=queue.connection)
        
        if job.is_finished:
            result = job.result
            if isinstance(result, dict) and result.get("error"):
                 return JsonResponse({'status': 'failed', 'message': result.get("message", "Erro desconhecido")})
            return JsonResponse({'status': 'finished', 'result': result})
        elif job.is_failed:
            return JsonResponse({'status': 'failed', 'message': 'A tarefa falhou ao ser executada.'})
        else:
            return JsonResponse({'status': job.get_status()}) # 'queued' or 'started'
            
    except Exception as e:
        return JsonResponse({'status': 'failed', 'message': str(e)}, status=500)

@login_required
def execute_trade_view(request):
    if request.method == 'POST':
        portfolio = Portfolio.objects.get(user=request.user)
        action = request.POST.get('action')
        ticker = request.POST.get('ticker')
        quantity = int(request.POST.get('quantity'))
        price_str = request.POST.get('price', '0').replace(',', '.')
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
    trade_history = portfolio.trade_history.order_by('timestamp')
    
    # Calcular KPIs
    total_trades = 0
    winning_trades = 0
    total_pl = Decimal('0.0')
    buy_operations = {}

    for trade in trade_history:
        if trade.side == 'BUY':
            if trade.ticker not in buy_operations:
                buy_operations[trade.ticker] = []
            buy_operations[trade.ticker].append(trade)
        elif trade.side == 'SELL':
            if trade.ticker in buy_operations and buy_operations[trade.ticker]:
                total_trades += 1
                buy_trade = buy_operations[trade.ticker].pop(0) # FIFO
                pl = (trade.price - buy_trade.price) * trade.quantity
                total_pl += pl
                if pl > 0:
                    winning_trades += 1
    
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0

    # Preparar dados para o gráfico
    chart_labels = []
    chart_data = []
    current_balance = portfolio.balance # Começa com o saldo atual
    
    # Simula o balanço "para trás" a partir do saldo atual e trades
    temp_balance = portfolio.balance
    positions_value = sum(pos.quantity * pos.buy_price for pos in portfolio.positions.all())
    initial_total_value = temp_balance + positions_value

    # Adiciona um ponto inicial
    if trade_history:
        start_date = trade_history.first().timestamp - timezone.timedelta(days=1)
        chart_labels.append(start_date.strftime('%d/%m/%Y'))
        # Tenta estimar um valor inicial
        # Esta é uma simplificação. Um cálculo mais preciso exigiria o saldo inicial no momento do cadastro.
        chart_data.append(float(initial_total_value - total_pl))


    for trade in trade_history:
        trade_value = trade.price * trade.quantity
        if trade.side == 'BUY':
            current_balance -= trade_value
        else:
            current_balance += trade_value
        
        chart_labels.append(trade.timestamp.strftime('%d/%m/%Y'))
        # O valor do portfólio é o saldo + valor das posições (simplificado aqui)
        # Para um gráfico preciso, precisaríamos de snapshots diários do valor das posições
        chart_data.append(float(current_balance))

    context = {
        'trade_history': reversed(trade_history), # Mostra os mais recentes primeiro na tabela
        'total_pl': total_pl,
        'win_rate': win_rate,
        'total_trades': total_trades,
        'chart_data': json.dumps({'labels': chart_labels, 'data': chart_data})
    }
    return render(request, 'trading_app/report.html', context)
