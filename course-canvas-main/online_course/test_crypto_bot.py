"""
Test script to verify crypto_bot integration
"""
import os
import sys
import django

# Setup Django environment
sys.path.insert(0, r'd:\Docx\python\Đề tài dự án 1\course-canvas-main\online_course')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'online_course.settings')
django.setup()

print("=" * 60)
print("✅ DJANGO SETUP SUCCESSFUL")
print("=" * 60)

# Test 1: Check if crypto_bot app is registered
from django.apps import apps
try:
    app_config = apps.get_app_config('crypto_bot')
    print(f"✅ crypto_bot app registered: {app_config.name}")
except LookupError as e:
    print(f"❌ crypto_bot app not found: {e}")

# Test 2: Check if model file exists
import os.path
model_path = r'd:\Docx\python\Đề tài dự án 1\course-canvas-main\online_course\crypto_bot\final_bi_lstm.keras'
if os.path.exists(model_path):
    print(f"✅ Model file exists: {model_path}")
else:
    print(f"❌ Model file not found: {model_path}")

# Test 3: Try to import utils
try:
    from crypto_bot.utils import predict_crypto
    print("✅ crypto_bot.utils imported successfully")
except Exception as e:
    print(f"❌ Error importing utils: {e}")

# Test 4: Try to import views
try:
    from crypto_bot import views
    print("✅ crypto_bot.views imported successfully")
    print(f"   Available views: btc_prediction, eth_prediction, crypto_home")
except Exception as e:
    print(f"❌ Error importing views: {e}")

# Test 5: Check URL patterns
try:
    from crypto_bot.urls import urlpatterns
    print(f"✅ URL patterns loaded: {len(urlpatterns)} patterns")
    for pattern in urlpatterns:
        print(f"   - {pattern.name}: {pattern.pattern}")
except Exception as e:
    print(f"❌ Error loading URLs: {e}")

print("=" * 60)
print("✅ INTEGRATION TEST COMPLETE")
print("=" * 60)
print("\n📋 NEXT STEPS:")
print("1. Run: python manage.py runserver")
print("2. Open browser: http://localhost:8000/crypto/")
print("3. Test BTC prediction: http://localhost:8000/crypto/btc/")
print("4. Test ETH prediction: http://localhost:8000/crypto/eth/")
