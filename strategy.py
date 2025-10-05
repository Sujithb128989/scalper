import pandas as pd
import numpy as np
import MetaTrader5 as mt5
from mt5_connector import get_market_data

# --- HELPER FUNCTIONS for Advanced Strategies ---

def is_fractal(df, i, lookback=2, fractal_type='resistance'):
    """
    Checks if a candle at index `i` is a fractal.
    A resistance fractal's high is higher than the `lookback` candles on both sides.
    A support fractal's low is lower than the `lookback` candles on both sides.
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
    Returns 'bullish' if a recent swing high is broken.
    Returns 'bearish' if a recent swing low is broken.
    """
    recent_high = df['high'].iloc[-lookback:-1].max()
    recent_low = df['low'].iloc[-lookback:-1].min()
    current_close = df['close'].iloc[-1]

    if current_close > recent_high:
        return 'bullish'
    if current_close < recent_low:
        return 'bearish'
    return None

# --- UPGRADED TRADING STRATEGIES ---

def check_5m_strategy(symbol):
    """
    UPGRADED 5m STRATEGY: Fractal-Based Support/Resistance
    Identifies significant S/R levels using fractals and enters on a touch.
    """
    rates = get_market_data(symbol, mt5.TIMEFRAME_M5, 200)
    if rates is None or len(rates) < 50:
        return None

    df = pd.DataFrame(rates)
    supports, resistances = get_fractal_levels(df.iloc[-50:]) # Check last 50 candles for levels

    if not supports and not resistances:
        print("[5m LOG] No fractal S/R levels found in the last 50 candles.")
        return None

    current_price = df['close'].iloc[-1]
    point = mt5.symbol_info(symbol).point

    # Find the closest support and resistance levels
    closest_support = min(supports, key=lambda x: abs(x - current_price)) if supports else None
    closest_resistance = min(resistances, key=lambda x: abs(x - current_price)) if resistances else None

    print(f"[5m LOG] Price: {current_price:.5f} | Closest Support: {closest_support or 'N/A'} | Closest Resistance: {closest_resistance or 'N/A'}")

    # Entry Logic: Trade if price is very close to a fractal level
    if closest_support and abs(current_price - closest_support) < (10 * point):
        print(f"[5m SIGNAL] Price is near fractal support. BUY signal.")
        return 'buy'
    if closest_resistance and abs(current_price - closest_resistance) < (10 * point):
        print(f"[5m SIGNAL] Price is near fractal resistance. SELL signal.")
        return 'sell'

    return None

def check_1m_strategy(symbol):
    """
    UPGRADED 1m STRATEGY: Qualified Fair Value Gap (FVG) with Break of Structure (BOS)
    Requires both an FVG and a confirming BOS before entering.
    """
    rates = get_market_data(symbol, mt5.TIMEFRAME_M1, 30)
    if rates is None or len(rates) < 20:
        return None

    df = pd.DataFrame(rates)
    point = mt5.symbol_info(symbol).point
    min_gap_size = 3 * point  # FVG must be at least 3 points wide

    # --- 1. Check for a recent Break of Structure (BOS) ---
    bos_direction = check_break_of_structure(df, lookback=15)
    if not bos_direction:
        print("[1m LOG] No recent Break of Structure found.")
        return None

    print(f"[1m LOG] Found a {bos_direction} Break of Structure.")

    # --- 2. Find the most recent FVG that aligns with the BOS ---
    fvg_level = None
    if bos_direction == 'bullish':
        # Look for a bullish FVG (gap between high of i-2 and low of i)
        for i in range(len(df) - 3, 2, -1):
            gap_bottom = df['high'].iloc[i-2]
            gap_top = df['low'].iloc[i]
            if gap_top > gap_bottom and (gap_top - gap_bottom) >= min_gap_size:
                fvg_level = (gap_top + gap_bottom) / 2
                print(f"[1m LOG] Found Bullish FVG with mid-point at {fvg_level:.5f}")
                break # Use the most recent one

    elif bos_direction == 'bearish':
        # Look for a bearish FVG (gap between low of i-2 and high of i)
        for i in range(len(df) - 3, 2, -1):
            gap_top = df['low'].iloc[i-2]
            gap_bottom = df['high'].iloc[i]
            if gap_top > gap_bottom and (gap_top - gap_bottom) >= min_gap_size:
                fvg_level = (gap_top + gap_bottom) / 2
                print(f"[1m LOG] Found Bearish FVG with mid-point at {fvg_level:.5f}")
                break # Use the most recent one

    if not fvg_level:
        print("[1m LOG] No FVG found aligning with the BOS.")
        return None

    # --- 3. Entry Logic: Trade if price retraces to the FVG's 50% level ---
    current_price = df['close'].iloc[-1]
    if bos_direction == 'bullish' and current_price <= fvg_level:
        print(f"[1m SIGNAL] Price has retraced to bullish FVG level. BUY signal.")
        return 'buy'
    if bos_direction == 'bearish' and current_price >= fvg_level:
        print(f"[1m SIGNAL] Price has retraced to bearish FVG level. SELL signal.")
        return 'sell'

    return None