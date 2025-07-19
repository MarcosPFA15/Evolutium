# synthesis_engine.py
import google.generativeai as genai
import json
from . import config
import logging
from google.generativeai.types import HarmCategory, HarmBlockThreshold

class SynthesisEngine:
    def  __init__(self, api_key=None):
        self.model = None
        try:
            # Prioriza a chave passada diretamente. Se não houver, busca no config.
            final_api_key = api_key if api_key else config.GEMINI_API_KEY

            if not final_api_key:
                raise ValueError("A chave de API do Gemini não foi fornecida ou encontrada no ambiente.")
            
            genai.configure(api_key=final_api_key)

            # --- BLOCO DE CÓDIGO CORRIGIDO: A DEFINIÇÃO ESTÁ DE VOLTA ---
            safety_settings = {
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
            # ---------------------------------------------------------

            self.model = genai.GenerativeModel('gemini-1.5-flash', safety_settings=safety_settings)
            logging.info("[ENGINE] Motor de Síntese com 'gemini-1.5-flash' inicializado com SUCESSO.")
        except Exception as e:
            logging.critical(f"[ENGINE] ERRO FATAL NA INICIALIZAÇÃO DO GEMINI: {e}", exc_info=True)
            raise

    def _format_value(self, value, is_percent=False, is_currency=False):
        if not isinstance(value, (int, float)): return "N/A"
        if is_percent: return f"{value * 100:.2f}%"
        if is_currency: return f"R$ {value:.2f}"
        return f"{value:.2f}"

    def _generate_content_safely(self, prompt: str) -> str:
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logging.error(f"[ENGINE] A chamada para a API do Gemini falhou: {e}")
            return ""

    def decide_best_investment(self, candidates: list, trade_history: list, market_context: dict) -> dict:
        if not self.model: return {"decision": "ERROR", "rationale": "Modelo não inicializado."}
        prompt = self._build_buy_prompt(candidates, trade_history, market_context)
        logging.info("[ENGINE] Enviando prompt de COMPRA para análise do Gemini...")
        response_text = self._generate_content_safely(prompt)
        return self._parse_response(response_text)

    def should_sell_position(self, position_data: dict, current_position: dict, trade_history: list, market_context: dict) -> dict:
        if not self.model: return {"decision": "ERROR", "rationale": "Modelo não inicializado."}
        prompt = self._build_sell_prompt(position_data, current_position, trade_history, market_context)
        logging.info(f"[ENGINE] Enviando prompt de VENDA para reavaliação de {current_position['ticker']}...")
        response_text = self._generate_content_safely(prompt)
        return self._parse_response(response_text)

    def _get_full_technical_analysis_text(self, fundamentals: dict, technicals: dict) -> str:
        if not technicals: return "\n  - Análise Técnica: Dados insuficientes."
        current_price = fundamentals.get('Preço Atual')
        if not current_price: return "\n  - Análise Técnica: Preço atual indisponível."
        analysis_items = []
        sma_21 = technicals.get('SMA_21')
        if sma_21:
            trend_21 = "alta" if current_price > sma_21 else "baixa"
            analysis_items.append(f"Tendência Curto Prazo: de {trend_21} (preço vs Média 21d).")
        sma_50 = technicals.get('SMA_50')
        if sma_50:
            trend_50 = "alta" if current_price > sma_50 else "baixa"
            analysis_items.append(f"Tendência Médio Prazo: de {trend_50} (preço vs Média 50d).")
        rsi = technicals.get('RSI_14')
        if rsi:
            rsi_signal = "Neutro"
            if rsi > 70: rsi_signal = "Sobrecomprado (sinal de possível venda/reversão)"
            elif rsi < 30: rsi_signal = "Sobrevendido (sinal de possível compra/reversão)"
            analysis_items.append(f"Momentum (RSI): {self._format_value(rsi)} ({rsi_signal}).")
        bbu = technicals.get('BBU_20_2.0')
        bbl = technicals.get('BBL_20_2.0')
        if bbu and bbl:
            vol_signal = "dentro das bandas"
            if current_price > bbu: vol_signal = "acima da banda superior (alerta de preço 'esticado')"
            elif current_price < bbl: vol_signal = "abaixo da banda inferior (alerta de preço 'descontado')"
            analysis_items.append(f"Volatilidade (Bandas de Bollinger): Preço {vol_signal}.")
        macd_line = technicals.get('MACD_12_26_9')
        signal_line = technicals.get('MACDs_12_26_9')
        if macd_line and signal_line:
            macd_signal = "alta (momentum positivo)" if macd_line > signal_line else "baixa (momentum negativo)"
            analysis_items.append(f"Convergência (MACD): Sinal de {macd_signal}.")
        if not analysis_items: return "\n  - Análise Técnica: Dados insuficientes."
        return "\n  - " + "\n  - ".join(analysis_items)

    def _build_buy_prompt(self, candidates: list, trade_history: list, market_context: dict) -> str:
        candidates_str = ""
        for data in candidates:
            fundamentals = data['fundamental_data']
            technicals = data.get('technical_indicators', {})
            technical_text = self._get_full_technical_analysis_text(fundamentals, technicals)
            candidates_str += f"""
            ---
            Candidato: {data['ticker']}
            - Preço Atual: {self._format_value(fundamentals.get('Preço Atual'), is_currency=True)}
            - Indicadores Fundamentalistas: P/L: {self._format_value(fundamentals.get('P/L'))}, ROE: {self._format_value(fundamentals.get('ROE'), is_percent=True)}
            - Análise Técnica Detalhada:{technical_text}
            - Notícias: {' | '.join(data['recent_news'])}
            """
        history_str = "\n".join([f"- {t['timestamp']}: {t['side']} {t['quantity']} {t['ticker']} @ R$ {t['price']:.2f}" for t in trade_history[-5:]])
        if not history_str: history_str = "Nenhuma transação recente."
        
        context_str = f"  - Ibovespa (última semana): {market_context.get('ibov_change', 'N/A')}\n"

        return f"""
        **Análise Comparativa de Portfólio para Seleção de Ativo**
        **Contexto Geral do Mercado:**
        {context_str}
        **Histórico de Transações Recentes (as 5 últimas):**
        {history_str}
        
        **Sua Tarefa:**
        1. Considere o contexto de mercado. Em um mercado de baixa (Ibovespa caindo), seja mais cauteloso. Em um mercado de alta, seja mais confiante.
        2. Analise os ativos candidatos abaixo, combinando análise fundamentalista, de notícias e técnica.
        3. **Use o histórico de transações para evitar "flip-flopping"**: não compre um ativo que foi vendido recentemente, a menos que haja uma nova e forte razão para isso.
        4. Escolha o melhor e único ativo para comprar. Se nenhum candidato apresentar uma combinação favorável, escolha "HOLD".
        
        **Ativos Candidatos:**{candidates_str}
        
        **IMPORTANTE: Sua resposta deve ser APENAS um objeto JSON com as chaves "decision" (string: "BUY" ou "HOLD"), "ticker" (string com o ticker escolhido, ou null), e "rationale" (string explicando a comparação).**
        """

    def _build_sell_prompt(self, data: dict, position: dict, trade_history: list, market_context: dict) -> str:
        fundamentals = data['fundamental_data']
        current_price = fundamentals.get('Preço Atual', 0)
        buy_price = position['buy_price']
        profit_loss_percent = ((current_price / buy_price) - 1) if buy_price > 0 and isinstance(current_price, (int, float)) else 0
        technicals = data.get('technical_indicators', {})
        technical_text = self._get_full_technical_analysis_text(fundamentals, technicals)
        history_str = "\n".join([f"- {t['timestamp']}: {t['side']} {t['quantity']} {t['ticker']} @ R$ {t['price']:.2f}" for t in trade_history[-5:]])
        if not history_str: history_str = "Nenhuma transação recente."

        context_str = f"  - Ibovespa (última semana): {market_context.get('ibov_change', 'N/A')}\n"

        return f"""
        **Reavaliação de Posição para Venda**
        **Contexto Geral do Mercado:**
        {context_str}
        **Histórico de Transações Recentes (as 5 últimas):**
        {history_str}

        **Sua Tarefa:**
        1. Analise o cenário completo da posição abaixo.
        2. Se o mercado geral está em forte queda (Ibovespa caindo), pode ser prudente realizar lucros ou cortar perdas mesmo em posições boas.
        3. **Considere o histórico:** se você acabou de comprar este ativo, a justificativa para vender precisa ser muito forte.

        **1. Dados da Sua Posição:**
        - Ativo: {data['ticker']}
        - Preço de Compra: {self._format_value(buy_price, is_currency=True)}
        - Preço Atual: {self._format_value(current_price, is_currency=True)}
        - Lucro/Prejuízo Atual: {self._format_value(profit_loss_percent, is_percent=True)}
        
        **2. Dados Atuais do Mercado para {data['ticker']}:**
        - Indicadores Fundamentalistas: P/L: {self._format_value(fundamentals.get('P/L'))}, ROE: {self._format_value(fundamentals.get('ROE'), is_percent=True)}
        - Análise Técnica Detalhada:{technical_text}
        - Notícias Recentes: {' | '.join(data['recent_news'])}
        
        **IMPORTANTE: Sua resposta deve ser APENAS um objeto JSON com as chaves "decision" (string: "SELL" ou "HOLD") e "rationale" (string).**
        """

    def _parse_response(self, response_text: str) -> dict:
        logging.debug(f"[ENGINE] Resposta bruta recebida do Gemini: '{response_text}'")
        if not response_text or not response_text.strip():
            return {"decision": "ERROR", "rationale": "Resposta vazia ou bloqueada pela API."}
        try:
            json_str = response_text.strip().replace("```json", "").replace("```", "").strip()
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logging.error(f"[ENGINE] Não foi possível processar o JSON da resposta do Gemini: {e}. Resposta: '{response_text}'")
            return {"decision": "ERROR", "rationale": "Falha ao processar o formato JSON da resposta."}

    def _build_buy_prompt_backtest(self, candidates: list, market_context: dict) -> str:
        candidates_str = ""
        for data in candidates:
            fundamentals = data['fundamental_data']
            technicals = data.get('technical_indicators', {})
            technical_text = self._get_full_technical_analysis_text(fundamentals, technicals)
            candidates_str += f"""
            ---
            Candidato: {data['ticker']}
            - Preço Atual: {self._format_value(fundamentals.get('Preço Atual'), is_currency=True)}
            - Análise Técnica Detalhada:{technical_text}
            """
        
        context_str = f"  - Ibovespa (última semana): {market_context.get('ibov_change', 'N/A')}\n"

        return f"""
        **Análise Comparativa para Backtest (Foco Técnico e Contexto)**
        **Contexto Geral do Mercado:**
        {context_str}
        **Sua Tarefa:**
        1. Considere o contexto de mercado. Em um mercado de baixa (Ibovespa caindo), seja mais seletivo e exija sinais técnicos mais fortes para comprar.
        2. Analise os dados puramente técnicos dos ativos candidatos.
        3. Um candidato ideal tem uma tendência de alta clara (preço acima das médias), um RSI que não esteja sobrecomprado (>70) e um sinal de MACD positivo.
        4. Escolha o melhor e único ativo para comprar com base APENAS nos indicadores técnicos e no contexto de mercado. Se nenhum for claramente positivo, escolha "HOLD".
        
        **Ativos Candidatos:**{candidates_str}
        
        **IMPORTANTE: Sua resposta deve ser APENAS um objeto JSON com as chaves "decision" (string: "BUY" ou "HOLD"), "ticker" (string com o ticker escolhido, ou null), e "rationale" (string explicando a comparação técnica).**
        """

    def decide_best_investment_backtest(self, candidates: list, market_context: dict) -> dict:
        if not self.model: return {"decision": "ERROR", "rationale": "Modelo não inicializado."}
        prompt = self._build_buy_prompt_backtest(candidates, market_context)
        logging.info("[ENGINE] Enviando prompt de COMPRA (modo backtest) para análise do Gemini...")
        response_text = self._generate_content_safely(prompt)
        return self._parse_response(response_text)