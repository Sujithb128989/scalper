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
    Finds all valid fractal levels and returns them in a single dictionary.
    Returns: {level: 'buy'/'sell'}
    """
    rates = get_market_data(symbol, mt5.TIMEFRAME_M5, 200)
    if rates is None or len(rates) < 50:
        return {}

    df = pd.DataFrame(rates)
    levels = {}

    # Check last 100 candles for levels
    for i in range(len(df) - 100, len(df)):
        if is_fractal(df, i, lookback=2, fractal_type='support'):
            levels[df['low'].iloc[i]] = 'buy'
        if is_fractal(df, i, lookback=2, fractal_type='resistance'):
            levels[df['high'].iloc[i]] = 'sell'

    print(f"[5m Strategy] Found {len(levels)} total fractal levels.")
    return levels

def find_qualified_fvg_levels_1m(symbol):
    """
    Finds qualified FVG levels confirmed by a BOS and returns them in a single dictionary.
    Returns: {level: 'buy'/'sell'}
    """
    rates = get_market_data(symbol, mt5.TIMEFRAME_M1, 30)
    if rates is None or len(rates) < 20:
        return {}

    df = pd.DataFrame(rates)
    point = mt5.symbol_info(symbol).point
    min_gap_size = 3 * point
    levels = {}

    bos_direction = check_break_of_structure(df, lookback=15)
    if not bos_direction:
        return {}

    print(f"[1m Strategy] Found a {bos_direction} Break of Structure.")

    if bos_direction == 'bullish':
        for i in range(len(df) - 3, 2, -1):
            gap_bottom = df['high'].iloc[i-2]
            gap_top = df['low'].iloc[i]
            if gap_top > gap_bottom and (gap_top - gap_bottom) >= min_gap_size:
                fvg_level = (gap_top + gap_bottom) / 2
                levels[fvg_level] = 'buy'
                print(f"[1m Strategy] Found Bullish FVG level at {fvg_level:.5f}")

    elif bos_direction == 'bearish':
        for i in range(len(df) - 3, 2, -1):
            gap_top = df['low'].iloc[i-2]
            gap_bottom = df['high'].iloc[i]
            if gap_top > gap_bottom and (gap_top - gap_bottom) >= min_gap_size:
                fvg_level = (gap_top + gap_bottom) / 2
                levels[fvg_level] = 'sell'
                print(f"[1m Strategy] Found Bearish FVG level at {fvg_level:.5f}")

    return levels