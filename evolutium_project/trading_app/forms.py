# trading_app/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    # ... (os outros campos continuam os mesmos) ...
    username = forms.CharField(
        label="Nome de Usuário",
        help_text="Obrigatório. 150 caracteres ou menos. Letras, números e @/./+/-/_ apenas."
    )
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
        initial=10000.00,
        help_text="Exemplo: 10000,00"
    )

    # --- NOVO CAMPO ADICIONADO ---
    terms_agreement = forms.BooleanField(
        label="Eu li e concordo com os termos de uso.",
        required=True,
        initial=False
    )
    # -----------------------------

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)