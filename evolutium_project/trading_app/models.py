# trading_app/models.py
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gemini_api_key = models.CharField(max_length=255, blank=True, null=True, verbose_name="Chave de API do Gemini")

    def __str__(self):
        return self.user.username

class Portfolio(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="Saldo em Conta")

    def __str__(self):
        return f"Portfólio de {self.user.username}"
    
class Position(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='positions')
    ticker = models.CharField(max_length=10)
    quantity = models.IntegerField()
    buy_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.ticker} @ {self.buy_price}"

class TradeHistory(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='trade_history')
    ticker = models.CharField(max_length=10)
    side = models.CharField(max_length=4) # 'BUY' ou 'SELL'
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.timestamp.strftime('%Y-%m-%d')}] {self.side} {self.ticker}"