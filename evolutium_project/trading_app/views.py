# trading_app/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal, InvalidOperation
import math
import yfinance as yf
from django.http import HttpResponseNotAllowed

from django.contrib.auth.forms import AuthenticationForm
from .models import Portfolio, UserProfile, Position, TradeHistory
from .forms import CustomUserCreationForm

# --- IMPORTAÇÕES CORRIGIDAS E FINALIZADAS ---
from core_logic.synthesis_engine import SynthesisEngine
from core_logic.data_provider import DataProvider
# Importa a constante específica que precisamos, para evitar qualquer ambiguidade
from core_logic.config import TICKERS_TO_MONITOR, RISK_PERCENTAGE_PER_TRADE
# ---------------------------------------------

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
    user_profile = UserProfile.objects.get(user=request.user)
    
    context = {
        'portfolio': portfolio,
        'positions': portfolio.positions.all(),
        'recommendation': None
    }

    if request.method == 'POST':
        api_key = user_profile.gemini_api_key
        if not api_key:
            messages.error(request, "Você precisa salvar sua chave de API do Gemini.")
            return render(request, 'trading_app/dashboard.html', context)
        try:
            synthesis_engine = SynthesisEngine(api_key=api_key)
            data_provider = DataProvider()
            
            ibov_hist = yf.Ticker("^BVSP").history(period="7d")
            change = (ibov_hist['Close'].iloc[-1] / ibov_hist['Close'].iloc[0]) - 1
            market_context = {"ibov_change": f"{change:.2%}"}
            
            trade_history_qs = portfolio.trade_history.order_by('-timestamp')[:5]
            trade_history = list(trade_history_qs.values('timestamp', 'ticker', 'side', 'quantity', 'price'))

            best_sell_recommendation = None
            for pos in portfolio.positions.all():
                market_data = data_provider.get_market_data(pos.ticker)
                if market_data:
                    current_pos_dict = {'ticker': pos.ticker, 'quantity': pos.quantity, 'buy_price': float(pos.buy_price)}
                    sell_decision = synthesis_engine.should_sell_position(market_data, current_pos_dict, trade_history, market_context)
                    if sell_decision.get("decision") == "SELL":
                        best_sell_recommendation = {
                            'action': 'SELL', 'ticker': pos.ticker, 'rationale': sell_decision.get('rationale'),
                            'quantity': pos.quantity, 'current_price': market_data['fundamental_data'].get('Preço Atual', 0)
                        }
                        break

            best_buy_recommendation = None
            if not best_sell_recommendation:
                tickers_in_portfolio = {p.ticker for p in portfolio.positions.all()}
                candidates = [data for ticker in TICKERS_TO_MONITOR if ticker not in tickers_in_portfolio and (data := data_provider.get_market_data(ticker))]
                if candidates:
                    buy_decision = synthesis_engine.decide_best_investment(candidates, trade_history, market_context)
                    if buy_decision.get("decision") == "BUY":
                        ticker = buy_decision.get('ticker')
                        asset_data = next((c for c in candidates if c['ticker'] == ticker), None)
                        price = asset_data['fundamental_data'].get('Preço Atual', 0) if asset_data else 0
                        if price > 0:
                            # Usa a constante importada diretamente
                            risk_value = portfolio.balance * Decimal(str(RISK_PERCENTAGE_PER_TRADE))
                            quantity = math.floor(risk_value / Decimal(str(price)))
                            
                            # Só cria a recomendação se a quantidade for maior que zero
                            if quantity > 0:
                                best_buy_recommendation = {
                                    'action': 'BUY', 'ticker': ticker, 'rationale': buy_decision.get('rationale'),
                                    'suggested_quantity': quantity, 'current_price': price
                                }

            if best_sell_recommendation:
                context['recommendation'] = best_sell_recommendation
            elif best_buy_recommendation:
                context['recommendation'] = best_buy_recommendation
            else:
                context['recommendation'] = {'action': 'HOLD', 'ticker': 'ALL', 'rationale': 'Nenhuma oportunidade clara de compra ou venda foi identificada no momento.'}

        except Exception as e:
            messages.error(request, f"Ocorreu um erro durante a análise: {e}")

    return render(request, 'trading_app/dashboard.html', context)

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
