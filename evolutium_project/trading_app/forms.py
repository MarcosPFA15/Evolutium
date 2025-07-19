# trading_app/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    # --- Sobrescrevendo os campos padrão do Django ---
    username = forms.CharField(
        label="Nome de Usuário",
        help_text="Letras, números e @/./+/-/_ apenas."
    )
    password2 = forms.CharField(
        label="Confirmação de Senha",
        widget=forms.PasswordInput,
        help_text="Informe a mesma senha para verificação."
    )
    
    # --- Customizando nossos campos ---
    email = forms.EmailField(
        label="Endereço de E-mail"
    )
    gemini_api_key = forms.CharField(
        label="Chave de API do Google Gemini",
        widget=forms.PasswordInput,
        help_text="Sua chave é armazenada de forma segura e não será exibida."
    )
    initial_balance = forms.DecimalField(
        label="Saldo Inicial para Simulação (R$)",
        min_value=0.01,
        decimal_places=2,
        initial=1000.00,
        help_text="Exemplo: 1000,00"
    )

    class Meta(UserCreationForm.Meta):
        model = User
        # A ordem dos campos no formulário
        fields = ('username', 'email', 'password21', 'password22', 'gemini_api_key', 'initial_balance')