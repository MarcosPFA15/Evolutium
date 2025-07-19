# data_provider.py
import yfinance as yf
import pandas as pd
import logging
import pandas_ta as ta

class DataProvider:
    # ... (A classe DataProvider para o modo "ao vivo" continua a mesma) ...
    def get_market_data(self, ticker: str) -> dict | None:
        yf_ticker_str = f"{ticker}.SA"
        logging.info(f"[DATA PROV] Buscando dados para {yf_ticker_str}...")
        try:
            yf_ticker = yf.Ticker(yf_ticker_str)
            info = yf_ticker.info
            if not info or 'currentPrice' not in info:
                logging.warning(f"[DATA PROV] Não foram encontrados dados para {yf_ticker_str}.")
                return None
            hist_df = yf_ticker.history(period="150d", interval="1d", auto_adjust=False)
            
            # Adicionado para garantir compatibilidade
            if isinstance(hist_df.columns, pd.MultiIndex):
                hist_df.columns = hist_df.columns.droplevel(1)

            technical_indicators = {}
            if not hist_df.empty and len(hist_df) > 50:
                hist_df.ta.sma(length=21, append=True)
                hist_df.ta.sma(length=50, append=True)
                hist_df.ta.rsi(length=14, append=True)
                hist_df.ta.bbands(length=20, append=True)
                hist_df.ta.macd(fast=12, slow=26, signal=9, append=True)
                last_row = hist_df.iloc[-1]
                technical_indicators = {
                    "SMA_21": last_row.get('SMA_21'), "SMA_50": last_row.get('SMA_50'),
                    "RSI_14": last_row.get('RSI_14'), "BBL_20_2.0": last_row.get('BBL_20_2.0'),
                    "BBU_20_2.0": last_row.get('BBU_20_2.0'), "MACD_12_26_9": last_row.get('MACD_12_26_9'),
                    "MACDh_12_26_9": last_row.get('MACDh_12_26_9'), "MACDs_12_26_9": last_row.get('MACDs_12_26_9'),
                }
            fundamentals = {
                "Preço Atual": info.get('currentPrice'), "P/L": info.get('trailingPE'),
                "ROE": info.get('returnOnEquity'), "Dívida/Patrimônio": info.get('debtToEquity'),
                "Dividend Yield": info.get('dividendYield'), "Margem Líquida": info.get('profitMargins'),
                "Setor": info.get('sector'), "Resumo": info.get('longBusinessSummary')
            }
            news = yf_ticker.news
            recent_news = [item['title'] for item in news[:5] if 'title' in item] if news else ["Nenhuma notícia recente encontrada."]
            logging.info(f"-> Dados para {ticker} obtidos com sucesso.")
            return {
                "ticker": ticker, "historical_data": hist_df, "fundamental_data": fundamentals,
                "recent_news": recent_news, "technical_indicators": technical_indicators
            }
        except Exception as e:
            logging.error(f"[DATA PROV] Falha ao obter dados do yfinance para {ticker}: {e}", exc_info=True)
            return None


class BacktestDataProvider:
    def __init__(self, tickers: list, start_date: str, end_date: str):
        self.tickers = tickers
        self.start_date = start_date
        self.end_date = end_date
        self.historical_data = self._preload_all_data()
        self.current_date = None

    def _preload_all_data(self) -> dict:
        logging.info(f"[BACKTEST DATA] Pré-carregando todos os dados de {self.start_date} a {self.end_date}...")
        all_data = {}
        for ticker in self.tickers:
            yf_ticker_str = f"{ticker}.SA"
            try:
                df = yf.download(yf_ticker_str, start=self.start_date, end=self.end_date, progress=False, auto_adjust=False)
                
                if df.empty:
                    logging.warning(f" -> Nenhum dado encontrado para {ticker} no período.")
                    continue

                # --- A SOLUÇÃO DEFINITIVA ---
                # Se as colunas forem um MultiIndex (tuplas), achata para um Index simples.
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.droplevel(1)
                # -----------------------------

                df.ta.sma(length=21, append=True)
                df.ta.sma(length=50, append=True)
                df.ta.rsi(length=14, append=True)
                df.ta.bbands(length=20, append=True)
                df.ta.macd(fast=12, slow=26, signal=9, append=True)
                
                all_data[ticker] = df
                logging.info(f" -> Dados para {ticker} carregados com sucesso.")
            except Exception as e:
                logging.error(f"Falha CRÍTICA ao carregar ou processar dados para {ticker}: {e}")
        return all_data

    def set_current_date(self, date):
        self.current_date = date

    def get_trading_days(self) -> pd.DatetimeIndex:
        if not self.historical_data:
            return pd.DatetimeIndex([])
        all_days = pd.DatetimeIndex([])
        for ticker in self.historical_data:
            all_days = all_days.union(self.historical_data[ticker].index)
        return all_days.sort_values()

    def get_market_data(self, ticker: str) -> dict | None:
        if ticker not in self.historical_data or self.current_date is None:
            return None
        df = self.historical_data[ticker]
        try:
            day_data = df.loc[self.current_date]
        except KeyError:
            return None
        current_price = day_data.get('Close')
        if pd.isna(current_price):
            return None
        technical_indicators = {
            "SMA_21": day_data.get('SMA_21'), "SMA_50": day_data.get('SMA_50'),
            "RSI_14": day_data.get('RSI_14'), "BBL_20_2.0": day_data.get('BBL_20_2.0'),
            "BBU_20_2.0": day_data.get('BBU_20_2.0'), "MACD_12_26_9": day_data.get('MACD_12_26_9'),
            "MACDh_12_26_9": day_data.get('MACDh_12_26_9'), "MACDs_12_26_9": day_data.get('MACDs_12_26_9'),
        }
        fundamentals = {"Preço Atual": current_price}
        return {
            "ticker": ticker, "fundamental_data": fundamentals,
            "technical_indicators": technical_indicators,
            "recent_news": ["Notícias não disponíveis em modo de backtest."]
        }