# trading_app/urls.py
from django.urls import path
from . import views

app_name = 'trading_app'

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # --- NOVAS ROTAS PARA AÇÕES ---
    path('execute_trade/', views.execute_trade_view, name='execute_trade'),
    path('update_balance/', views.update_balance_view, name='update_balance'),
]