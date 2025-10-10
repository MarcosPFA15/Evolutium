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
    path('report/', views.report_view, name='report'), # Nova rota para relatórios

    # Rotas para operações
    path('execute_trade/', views.execute_trade_view, name='execute_trade'),
    path('update_balance/', views.update_balance_view, name='update_balance'),

    # Rotas para análise assíncrona com IA
    path('start_analysis/', views.start_analysis_view, name='start_analysis'),
    path('check_analysis_result/<str:job_id>/', views.check_analysis_result_view, name='check_analysis_result'),
]
