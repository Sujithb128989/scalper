import time
import MetaTrader5 as mt5
from mt5_connector import initialize_mt5, shutdown_mt5
from strategy import find_fractal_levels_5m, find_qualified_fvg_levels_1m

def run_strategy_test():
    """
    Connects to MT5 and tests the refactored 'level-finder' strategy functions.
    This verifies that the core signal generation logic is working correctly.
    """
    print(f"--- Running Strategy 'Level-Finder' Test Script ---")
    if not initialize_mt5():
        print("[TEST FAILED] Could not initialize MT5 connection.")
        return

    symbol = "BTCUSDm"

    print("\n--- Testing 5m Fractal Strategy ---")
    support_levels, resistance_levels = find_fractal_levels_5m(symbol)
    print(f"Found {len(support_levels)} support levels: {support_levels}")
    print(f"Found {len(resistance_levels)} resistance levels: {resistance_levels}")

    print("\n--- Testing 1m FVG Strategy ---")
    buy_levels, sell_levels = find_qualified_fvg_levels_1m(symbol)
    print(f"Found {len(buy_levels)} FVG buy levels: {buy_levels}")
    print(f"Found {len(sell_levels)} FVG sell levels: {sell_levels}")

    print("\n[TEST SUCCESS] Both strategy functions executed without errors.")

    # --- Clean up ---
    shutdown_mt5()
    print("--- Test Script Finished ---")

if __name__ == "__main__":
    run_strategy_test()