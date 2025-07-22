# core_logic/risk_manager.py
from . import config # <-- A IMPORTAÇÃO CORRETA E DEFINITIVA
import logging

def is_trade_allowed(account_balance: float, open_positions: list, ticker_to_trade: str, trade_value: float, side: str) -> bool:
    """Verifica as regras de segurança antes de permitir uma operação."""
    logging.info("[RISCO] Verificando regras de segurança...")

    if side == 'BUY':
        max_value_per_trade = account_balance * config.RISK_PERCENTAGE_PER_TRADE
        if trade_value > max_value_per_trade:
            logging.warning(f"[RISCO] COMPRA NEGADA: Valor (R$ {trade_value:,.2f}) excede o limite de risco por operação de R$ {max_value_per_trade:,.2f}.")
            return False

        position_exists = any(pos.ticker == ticker_to_trade for pos in open_positions)
        if position_exists:
            logging.warning(f"[RISCO] COMPRA NEGADA: Posição em {ticker_to_trade} já existe.")
            return False

    elif side == 'SELL':
        position_exists = any(pos.ticker == ticker_to_trade for pos in open_positions)
        if not position_exists:
            logging.error(f"[RISCO] VENDA NEGADA: Tentativa de vender {ticker_to_trade} sem ter a posição em carteira.")
            return False

    logging.info("[RISCO] APROVADO.")
    return True
