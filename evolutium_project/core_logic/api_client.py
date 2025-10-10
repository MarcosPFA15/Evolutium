import requests
import json
import time
import numpy as np
import logging
import os

class BTGAPIClient:
    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key
        self.session = requests.Session()
        self.balance_file = "simulated_balance.json"

    def get_account_balance(self) -> float | None:
        logging.info("[API SIMULADA] Buscando saldo da conta...")
        try:
            if not os.path.exists(self.balance_file):
                logging.warning(f"[API SIMULADA] -> Arquivo '{self.balance_file}' não encontrado. Criando com saldo inicial de 50000.00.")
                with open(self.balance_file, 'w') as f:
                    json.dump({"balance": 50000.00}, f, indent=4)
            
            with open(self.balance_file, 'r') as f:
                data = json.load(f)
                balance = float(data['balance'])
                logging.info(f"[API SIMULADA] -> Saldo encontrado: R$ {balance:,.2f}")
                return balance
        except (IOError, json.JSONDecodeError, KeyError, ValueError) as e:
            logging.error(f"[API SIMULADA] Falha ao ler o arquivo de saldo simulado: {e}", exc_info=True)
            return None
    def update_account_balance(self, new_balance: float):
        """
        Simula a atualização do saldo na corretora após uma operação.
        Escreve o novo saldo no arquivo de controle.
        """
        logging.info(f"[API SIMULADA] Atualizando saldo externo para R$ {new_balance:,.2f}...")
        try:
            with open(self.balance_file, 'w') as f:
                json.dump({"balance": new_balance}, f, indent=4)
            logging.info("[API SIMULADA] -> Saldo externo atualizado com sucesso.")
        except IOError as e:
            logging.error(f"[API SIMULADA] Falha ao escrever no arquivo de saldo simulado: {e}")

    def send_order(self, ticker: str, quantity: int, side: str, price: float) -> dict:
        logging.info(f"[API SIMULADA] Enviando ordem: {side} {quantity} {ticker} @ R$ {price:.2f}")
        time.sleep(0.5)
        order_id = f"sim_ord_{int(time.time())}"
        logging.info(f"-> Ordem {order_id} preenchida (FILLED).")
        return {"order_id": order_id, "status": "FILLED"}