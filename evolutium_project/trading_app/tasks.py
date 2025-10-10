# trading_app/tasks.py
import math
from decimal import Decimal
from .models import Portfolio, UserProfile
from core_logic.synthesis_engine import SynthesisEngine
from core_logic.data_provider import DataProvider
from core_logic.config import TICKERS_TO_MONITOR, RISK_PERCENTAGE_PER_TRADE
import yfinance as yf
import logging

def perform_full_analysis(user_id):
    """
    Tarefa pesada que roda em segundo plano para analisar o portfólio.
    """
    logging.info(f"Iniciando análise para o usuário {user_id}...")
    try:
        user_profile = UserProfile.objects.get(user_id=user_id)
        portfolio = Portfolio.objects.get(user_id=user_id)
        api_key = user_profile.gemini_api_key

        if not api_key:
            raise ValueError("A chave de API do Gemini não foi encontrada para este usuário.")

        synthesis_engine = SynthesisEngine(api_key=api_key)
        data_provider = DataProvider()
        
        # Contexto de mercado
        ibov_hist = yf.Ticker("^BVSP").history(period="7d")
        if ibov_hist.empty:
            market_context = {"ibov_change": "N/A"}
        else:
            change = (ibov_hist['Close'].iloc[-1] / ibov_hist['Close'].iloc[0]) - 1
            market_context = {"ibov_change": f"{change:.2%}"}
        
        # Histórico de transações
        trade_history_qs = portfolio.trade_history.order_by('-timestamp')[:5]
        trade_history = list(trade_history_qs.values('timestamp', 'ticker', 'side', 'quantity', 'price'))

        # 1. Avaliar Venda de Posições Atuais
        for pos in portfolio.positions.all():
            market_data = data_provider.get_market_data(pos.ticker)
            if market_data:
                current_pos_dict = {'ticker': pos.ticker, 'quantity': pos.quantity, 'buy_price': float(pos.buy_price)}
                sell_decision = synthesis_engine.should_sell_position(market_data, current_pos_dict, trade_history, market_context)
                if sell_decision.get("decision") == "SELL":
                    logging.info(f"Recomendação de VENDA para {pos.ticker} para o usuário {user_id}.")
                    return {
                        'action': 'SELL', 'ticker': pos.ticker, 'rationale': sell_decision.get('rationale'),
                        'quantity': pos.quantity, 'current_price': market_data['fundamental_data'].get('Preço Atual', 0)
                    }

        # 2. Se não houver venda, procurar por Compra
        tickers_in_portfolio = {p.ticker for p in portfolio.positions.all()}
        candidates = [data for ticker in TICKERS_TO_MONITOR if ticker not in tickers_in_portfolio and (data := data_provider.get_market_data(ticker))]
        if candidates:
            buy_decision = synthesis_engine.decide_best_investment(candidates, trade_history, market_context)
            if buy_decision.get("decision") == "BUY":
                ticker = buy_decision.get('ticker')
                asset_data = next((c for c in candidates if c['ticker'] == ticker), None)
                price = asset_data['fundamental_data'].get('Preço Atual', 0) if asset_data else 0
                if price > 0:
                    risk_value = portfolio.balance * Decimal(str(RISK_PERCENTAGE_PER_TRADE))
                    quantity = math.floor(risk_value / Decimal(str(price)))
                    if quantity > 0:
                        logging.info(f"Recomendação de COMPRA para {ticker} para o usuário {user_id}.")
                        return {
                            'action': 'BUY', 'ticker': ticker, 'rationale': buy_decision.get('rationale'),
                            'suggested_quantity': quantity, 'current_price': price
                        }
        
        # 3. Se nenhuma ação for encontrada, manter
        logging.info(f"Nenhuma oportunidade clara encontrada. Recomendação: HOLD para o usuário {user_id}.")
        return {'action': 'HOLD', 'ticker': 'ALL', 'rationale': 'Nenhuma oportunidade clara de compra ou venda foi identificada no momento.'}

    except Exception as e:
        logging.error(f"Falha na análise em segundo plano para o usuário {user_id}: {e}", exc_info=True)
        # Retorna um dicionário de erro para ser tratado no frontend
        return {"error": True, "message": str(e)}
