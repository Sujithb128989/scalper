import pandas as pd
import MetaTrader5 as mt5
from mt5_connector import get_market_data

def check_5m_strategy(symbol):
    """
    Checks for a trade signal based on the 5m support/resistance strategy.
    """
    rates = get_market_data(symbol, mt5.TIMEFRAME_M5, 200)
    if rates is None:
        return None

    df = pd.DataFrame(rates)

    support = df['low'].rolling(window=50).min().iloc[-1]
    resistance = df['high'].rolling(window=50).max().iloc[-1]
    current_price = df['close'].iloc[-1]
    point = mt5.symbol_info(symbol).point

    print(f"[5m LOG] Current Price: {current_price:.5f} | Support: {support:.5f} | Resistance: {resistance:.5f}")

    if abs(current_price - support) < (5 * point):
        print(f"[5m SIGNAL] Price {current_price:.5f} is near Support {support:.5f}. BUY signal.")
        return 'buy'
    elif abs(current_price - resistance) < (5 * point):
        print(f"[5m SIGNAL] Price {current_price:.5f} is near Resistance {resistance:.5f}. SELL signal.")
        return 'sell'

    return None

def check_1m_strategy(symbol):
    """
    Checks for a trade signal based on the 1m imbalance candle strategy.
    """
    rates = get_market_data(symbol, mt5.TIMEFRAME_M1, 5)
    if rates is None or len(rates) < 4:
        return None

    df = pd.DataFrame(rates)

    candle_minus_3 = df.iloc[-4]
    candle_minus_1 = df.iloc[-2]
    current_price = df['close'].iloc[-1]

    # Bullish Imbalance Check
    if candle_minus_1['low'] > candle_minus_3['high']:
        imbalance_top = candle_minus_1['low']
        imbalance_bottom = candle_minus_3['high']
        imbalance_mid_point = (imbalance_top + imbalance_bottom) / 2
        print(f"[1m LOG] Bullish Imbalance detected. Mid-point: {imbalance_mid_point:.5f}. Current Price: {current_price:.5f}")

        if current_price <= imbalance_mid_point:
            print(f"[1m SIGNAL] Price {current_price:.5f} has retraced to Bullish Imbalance mid-point {imbalance_mid_point:.5f}. BUY signal.")
            return 'buy'

    # Bearish Imbalance Check
    elif candle_minus_1['high'] < candle_minus_3['low']:
        imbalance_top = candle_minus_3['low']
        imbalance_bottom = candle_minus_1['high']
        imbalance_mid_point = (imbalance_top + imbalance_bottom) / 2
        print(f"[1m LOG] Bearish Imbalance detected. Mid-point: {imbalance_mid_point:.5f}. Current Price: {current_price:.5f}")

        if current_price >= imbalance_mid_point:
            print(f"[1m SIGNAL] Price {current_price:.5f} has retraced to Bearish Imbalance mid-point {imbalance_mid_point:.5f}. SELL signal.")
            return 'sell'

    else:
        print("[1m LOG] No recent imbalance pattern detected.")

    return None