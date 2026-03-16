import numpy as np
import pandas as pd
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import load_model
import mplfinance as mpm
import os

# Load model once when module is imported
model_path = os.path.join(os.path.dirname(__file__), 'final_bi_lstm.keras')
model = None

def get_model():
    """Load model lazily to avoid loading multiple times"""
    global model
    if model is None:
        model = load_model(model_path, compile=False)
    return model


def calculate_rsi(series, period=14):
    """Calculate RSI indicator"""
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def predict_crypto(symbol, days_ahead=60):
    """
    Predict cryptocurrency price for the next N days
    
    Args:
        symbol: Cryptocurrency symbol (e.g., 'BTC-USD', 'ETH-USD')
        days_ahead: Number of days to predict
    
    Returns:
        dict: Prediction results including current price, predicted price, 
              change percentage, trend, and chart image path
    """
    try:
        # Load model
        model = get_model()
        
        # ===== LOAD DATA =====
        data = yf.download(symbol, period="180d", interval="1d")
        data.dropna(inplace=True)
        
        # Flatten nếu MultiIndex
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        
        # Ép float sạch
        data = data[['Open','High','Low','Close','Volume']].astype(float)
        
        # ===== INDICATORS =====
        data['RSI'] = calculate_rsi(data['Close'])
        data['MA20'] = data['Close'].rolling(20).mean()
        data.dropna(inplace=True)
        
        # ===== FEATURES =====
        features = data[['Open','High','Low','Close','Volume','RSI','MA20']].values
        
        scaler = MinMaxScaler()
        scaled_data = scaler.fit_transform(features)
        
        close_scaler = MinMaxScaler()
        close_scaler.fit(features[:,3].reshape(-1,1))
        
        last_60 = scaled_data[-60:]
        predictions = []
        current_batch = last_60.copy()
        
        # ===== FORECAST LOOP =====
        for _ in range(days_ahead):
            X_test = np.reshape(current_batch, (1,60,7))
            pred = model.predict(X_test, verbose=0)
            
            pred_price = close_scaler.inverse_transform(pred)[0][0]
            predictions.append(pred_price)
            
            new_row = current_batch[-1].copy()
            new_row[3] = scaler.transform(
                [[0,0,0,pred_price,0,0,0]]
            )[0][3]
            
            current_batch = np.vstack([current_batch[1:], new_row])
        
        current_price = float(data['Close'].iloc[-1])
        final_prediction = float(predictions[-1])
        
        # Calculate change and trend
        change_percent = ((final_prediction - current_price) / current_price) * 100
        trend = "Tăng" if change_percent > 0 else "Giảm"
        trend_icon = "📈" if change_percent > 0 else "📉"
        
        # ===== VẼ BIỂU ĐỒ =====
        df_plot = data[['Open','High','Low','Close','Volume']].copy()
        df_plot.index = pd.to_datetime(df_plot.index)
        df_plot.index.name = "Date"
        
        future_dates = pd.date_range(
            start=df_plot.index[-1],
            periods=days_ahead+1,
            freq='D'
        )[1:]
        
        # Tạo nến forecast giả
        prev_close = df_plot['Close'].iloc[-1]
        future_rows = []
        
        for price in predictions:
            open_p = prev_close
            close_p = price
            high_p = max(open_p, close_p)
            low_p = min(open_p, close_p)
            
            future_rows.append([open_p, high_p, low_p, close_p, 0])
            prev_close = close_p
        
        future_df = pd.DataFrame(
            future_rows,
            columns=['Open','High','Low','Close','Volume'],
            index=future_dates
        )
        
        df_full = pd.concat([df_plot, future_df])
        
        # ===== ZOOM 120 NẾN GẦN NHẤT =====
        df_view = df_full.tail(120)
        
        # ===== TÍNH LẠI MA20 =====
        ma20_view = df_view['Close'].rolling(20).mean()
        
        mc = mpm.make_marketcolors(
            up='#26a69a',
            down='#ef5350',
            wick='inherit',
            edge='inherit',
            volume='inherit'
        )
        
        s = mpm.make_mpf_style(
            base_mpf_style='nightclouds',
            marketcolors=mc,
            gridstyle='--'
        )
        
        apds = [
            mpm.make_addplot(ma20_view, color='orange')
        ]
        
        # Save chart to media folder
        from django.conf import settings
        import os
        
        # Create directory if it doesn't exist
        chart_dir = os.path.join(settings.MEDIA_ROOT, 'crypto_charts')
        os.makedirs(chart_dir, exist_ok=True)
        
        # Generate unique filename
        import time
        timestamp = int(time.time())
        chart_filename = f"{symbol.replace('-', '_')}_{timestamp}.png"
        chart_path = os.path.join(chart_dir, chart_filename)
        
        mpm.plot(
            df_view,
            type='candle',
            style=s,
            addplot=apds,
            volume=True,
            figsize=(14,8),
            tight_layout=True,
            title=f"{symbol} {days_ahead}-Day Forecast",
            savefig=chart_path
        )
        
        # Return relative URL for template
        chart_url = f"{settings.MEDIA_URL}crypto_charts/{chart_filename}"
        
        return {
            'success': True,
            'symbol': symbol,
            'current_price': current_price,
            'predicted_price': final_prediction,
            'change_percent': abs(change_percent),
            'trend': trend,
            'trend_icon': trend_icon,
            'chart_url': chart_url,
            'days_ahead': days_ahead
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
