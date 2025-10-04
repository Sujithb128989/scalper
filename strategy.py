import pandas as pd
import MetaTrader5 as mt5
from mt5_connector import get_market_data

def check_5m_strategy(symbol):
    """
    Checks for a trade signal based on the 5m support/resistance strategy.
    A trade is entered when the price touches a recent support or resistance level.

    Returns:
        'buy', 'sell', or None
    """
    # Fetch 5m data
    rates = get_market_data(symbol, mt5.TIMEFRAME_M5, 200) # Use more data for better levels
    if rates is None:
        return None

    df = pd.DataFrame(rates)

    # Identify support and resistance from recent pivot lows/highs
    support = df['low'].rolling(window=50).min().iloc[-1]
    resistance = df['high'].rolling(window=50).max().iloc[-1]

    current_price = df['close'].iloc[-1]
    point = mt5.symbol_info(symbol).point

    # Check if price is very close to support/resistance (within 5 points)
    if abs(current_price - support) < (5 * point): # Touch support
        return 'buy'
    elif abs(current_price - resistance) < (5 * point): # Touch resistance
        return 'sell'

    return None

def check_1m_strategy(symbol):
    """
    Checks for a trade signal based on the 1m imbalance candle strategy.
    An imbalance (or Fair Value Gap) is identified in the most recent candles,
    and a trade is entered at the 50% level of that imbalance.

    Returns:
        'buy', 'sell', or None
    """
    # Fetch the last 5 1m candles. We only need the last 3 for the pattern,
    # but we fetch a couple more for context.
    rates = get_market_data(symbol, mt5.TIMEFRAME_M1, 5)
    if rates is None or len(rates) < 4: # Need at least 4 candles to check the pattern including the current one
        return None

    df = pd.DataFrame(rates)

    # --- Focus only on the most recent 3-candle formation ---
    # The pattern is formed by the 3rd, 2nd, and 1st to last candles.
    # The current (last) candle is used to check for entry.

    candle_minus_3 = df.iloc[-4] # The candle before the pattern
    candle_minus_1 = df.iloc[-2] # The candle after the pattern
    current_price = df['close'].iloc[-1]

    # Bullish Imbalance (Fair Value Gap)
    # The low of candle[-2] is higher than the high of candle[-4]
    if candle_minus_1['low'] > candle_minus_3['high']:
        imbalance_top = candle_minus_1['low']
        imbalance_bottom = candle_minus_3['high']
        imbalance_mid_point = (imbalance_top + imbalance_bottom) / 2

        # If the current price has retraced to the 50% level, enter buy
        if current_price <= imbalance_mid_point:
            return 'buy'

    # Bearish Imbalance (Fair Value Gap)
    # The high of candle[-2] is lower than the low of candle[-4]
    if candle_minus_1['high'] < candle_minus_3['low']:
        imbalance_top = candle_minus_3['low']
        imbalance_bottom = candle_minus_1['high']
        imbalance_mid_point = (imbalance_top + imbalance_bottom) / 2

        # If the current price has retraced to the 50% level, enter sell
        if current_price >= imbalance_mid_point:
            return 'sell'

    return None