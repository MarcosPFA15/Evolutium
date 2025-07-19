from core_logic.synthesis_engine import SynthesisEngine
from core_logic.data_provider import DataProvider
from core_logic import config
import yfinance as yf
from .models import UserProfile
import json

def run_portfolio_analysis(user_id):
    """
    Esta é a nossa tarefa pesada que rodará em segundo plano.
    """
    try:
        user_profile = UserProfile.objects.get(user_id=user_id)
        api_key = user_profile.gemini_api_key

        synthesis_engine = SynthesisEngine(api_key=api_key)
        data_provider = DataProvider()

        candidates = [data for ticker in config.TICKERS_TO_MONITOR if (data := data_provider.get_market_data(ticker))]
        
        ibov_hist = yf.Ticker("^BVSP").history(period="7d")
        change = (ibov_hist['Close'].iloc[-1] / ibov_hist['Close'].iloc[0]) - 1
        market_context = {"ibov_change": f"{change:.2%}"}

        action_plan = synthesis_engine.get_portfolio_optimization_plan([], candidates, market_context)

        print(f"Análise para usuário {user_id} concluída. Plano: {action_plan}")
        

        return f"Análise para usuário {user_id} concluída com sucesso."
    except Exception as e:
        return f"Falha na análise para usuário {user_id}: {e}"