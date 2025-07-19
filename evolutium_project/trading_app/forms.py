# trading_app/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    gemini_api_key = forms.CharField(
        label="Chave de API do Google Gemini",
        widget=forms.PasswordInput,
        help_text="Sua chave é armazenada de forma segura e não será exibida."
    )
    initial_balance = forms.DecimalField(
        label="Saldo Inicial para Simulação (R$)",
        min_value=0.01,
        decimal_places=2,
        initial=10000.00
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)