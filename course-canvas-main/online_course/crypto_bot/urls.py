from django.urls import path
from . import views

app_name = 'crypto_bot'

urlpatterns = [
    # Trang chủ Crypto Bot
    path('', views.crypto_home, name='home'),
    
    # Dự đoán BTC
    path('btc/', views.btc_prediction, name='btc_prediction'),
    
    # Dự đoán ETH
    path('eth/', views.eth_prediction, name='eth_prediction'),
]
