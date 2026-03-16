from django.shortcuts import render
from django.http import JsonResponse
from .utils import predict_crypto


def crypto_home(request):
    """Trang chủ của Crypto Bot - Hiển thị cả BTC và ETH"""
    return render(request, 'crypto_bot/home.html')


def btc_prediction(request):
    """Dự đoán BTC 60 ngày"""
    result = predict_crypto('BTC-USD', days_ahead=60)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # AJAX request
        return JsonResponse(result)
    
    # Regular request
    context = {
        'result': result,
        'crypto_name': 'Bitcoin (BTC)',
        'symbol': 'BTC-USD'
    }
    return render(request, 'crypto_bot/prediction.html', context)


def eth_prediction(request):
    """Dự đoán ETH 60 ngày"""
    result = predict_crypto('ETH-USD', days_ahead=60)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # AJAX request
        return JsonResponse(result)
    
    # Regular request
    context = {
        'result': result,
        'crypto_name': 'Ethereum (ETH)',
        'symbol': 'ETH-USD'
    }
    return render(request, 'crypto_bot/prediction.html', context)
