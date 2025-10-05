import pandas as pd
import numpy as np
import MetaTrader5 as mt5
from mt5_connector import get_market_data

# --- HELPER FUNCTIONS for Advanced Strategies ---

def is_fractal(df, i, lookback=2, fractal_type='resistance'):
    """
    Checks if a candle at index `i` is a fractal.
    """
    if i < lookback or i > len(df) - 1 - lookback:
        return False

    if fractal_type == 'resistance':
        pivot_high = df['high'].iloc[i]
        for j in range(1, lookback + 1):
            if df['high'].iloc[i-j] >= pivot_high or df['high'].iloc[i+j] >= pivot_high:
                return False
        return True

    if fractal_type == 'support':
        pivot_low = df['low'].iloc[i]
        for j in range(1, lookback + 1):
            if df['low'].iloc[i-j] <= pivot_low or df['low'].iloc[i+j] <= pivot_low:
                return False
        return True

    return False

def get_fractal_levels(df, lookback=5):
    """
    Identifies all fractal support and resistance levels in the dataframe.
    """
    supports, resistances = [], []
    for i in range(len(df)):
        if is_fractal(df, i, lookback=2, fractal_type='support'):
            supports.append(df['low'].iloc[i])
        if is_fractal(df, i, lookback=2, fractal_type='resistance'):
            resistances.append(df['high'].iloc[i])
    return supports, resistances

def check_break_of_structure(df, lookback=15):
    """
    Checks for a Break of Structure (BOS).
    """
    recent_high = df['high'].iloc[-lookback:-1].max()
    recent_low = df['low'].iloc[-lookback:-1].min()
    current_close = df['close'].iloc[-1]

    if current_close > recent_high:
        return 'bullish'
    if current_close < recent_low:
        return 'bearish'
    return None

# --- REFACTORED STRATEGIES (Level Finders) ---

def find_fractal_levels_5m(symbol):
    """
    Finds all valid fractal support and resistance levels on the 5m chart.
    Returns two lists: (supports, resistances).
    """
    rates = get_market_data(symbol, mt5.TIMEFRAME_M5, 200)
    if rates is None or len(rates) < 50:
        return [], []

    df = pd.DataFrame(rates)
    supports, resistances = get_fractal_levels(df.iloc[-100:]) # Check last 100 candles

    print(f"[5m Strategy] Found {len(supports)} support levels and {len(resistances)} resistance levels.")
    return supports, resistances

def find_qualified_fvg_levels_1m(symbol):
    """
    Finds qualified FVG levels on the 1m chart that are confirmed by a BOS.
    Returns two lists: (buy_levels, sell_levels).
    """
    rates = get_market_data(symbol, mt5.TIMEFRAME_M1, 30)
    if rates is None or len(rates) < 20:
        return [], []

    df = pd.DataFrame(rates)
    point = mt5.symbol_info(symbol).point
    min_gap_size = 3 * point

    bos_direction = check_break_of_structure(df, lookback=15)
    if not bos_direction:
        return [], []

    print(f"[1m Strategy] Found a {bos_direction} Break of Structure.")

    buy_levels, sell_levels = [], []
    if bos_direction == 'bullish':
        for i in range(len(df) - 3, 2, -1):
            gap_bottom = df['high'].iloc[i-2]
            gap_top = df['low'].iloc[i]
            if gap_top > gap_bottom and (gap_top - gap_bottom) >= min_gap_size:
                fvg_level = (gap_top + gap_bottom) / 2
                buy_levels.append(fvg_level)
                print(f"[1m Strategy] Found Bullish FVG level at {fvg_level:.5f}")
                # We can add multiple levels if they exist

    elif bos_direction == 'bearish':
        for i in range(len(df) - 3, 2, -1):
            gap_top = df['low'].iloc[i-2]
            gap_bottom = df['high'].iloc[i]
            if gap_top > gap_bottom and (gap_top - gap_bottom) >= min_gap_size:
                fvg_level = (gap_top + gap_bottom) / 2
                sell_levels.append(fvg_level)
                print(f"[1m Strategy] Found Bearish FVG level at {fvg_level:.5f}")

    return buy_levels, sell_levels