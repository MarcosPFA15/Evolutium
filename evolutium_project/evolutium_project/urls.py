# evolutium_project/urls.py
from django.contrib import admin
from django.urls import path, include # Adicione 'include'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('trading_app.urls')), # Inclui todas as URLs do nosso app
]