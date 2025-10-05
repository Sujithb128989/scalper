import time
import MetaTrader5 as mt5
from mt5_connector import initialize_mt5, shutdown_mt5
from trader import open_trade, close_trade
from strategy import find_fractal_levels_5m, find_qualified_fvg_levels_1m
from config import MAGIC_NUMBER, TP_SL_UNITS, MAX_TRADES, LOT_SIZES

def run_full_stress_test():
    """
    Performs the user-defined stress test:
    1. Finds and displays all potential trade levels for verification.
    2. Immediately attempts to open MAX_TRADES positions.
    3. Live-monitors all opened trades until they are closed by the P/L logic.
    """
    print(f"--- Running Full Stress Test ---")
    if not initialize_mt5():
        print("[TEST FAILED] Could not initialize MT5 connection.")
        return

    symbol = "BTCUSDm"
    lot_size = LOT_SIZES.get(symbol)

    # --- Step 1: Find and display levels for verification ---
    print("\n--- Finding all potential strategy levels... ---")
    fractal_levels = find_fractal_levels_5m(symbol)
    fvg_levels = find_qualified_fvg_levels_1m(symbol)
    print(f"Found {len(fractal_levels)} fractal levels: {fractal_levels}")
    print(f"Found {len(fvg_levels)} FVG levels: {fvg_levels}")

    # --- Step 2: Immediately attempt to open trades ---
    print(f"\n--- Stress Test: Attempting to open up to {MAX_TRADES} trades of {lot_size} lots... ---")
    for i in range(MAX_TRADES):
        print(f"Attempting to open trade {i + 1}/{MAX_TRADES}...")
        open_trade('buy', symbol)
        time.sleep(0.2)

    # --- Step 3: Verify trades and enter monitoring loop ---
    initial_positions = mt5.positions_get(symbol=symbol, magic=MAGIC_NUMBER)
    num_opened = len(initial_positions or [])

    if num_opened == 0:
        print("[TEST FAILED] Could not open a single trade. Please check account margin or logs.")
        shutdown_mt5()
        return

    print(f"\nSuccessfully opened {num_opened} trades. Entering live monitoring mode...")
    print(f"This test will run until all {num_opened} positions are closed by hitting the +/- ${TP_SL_UNITS} target.")

    try:
        while True:
            positions = mt5.positions_get(symbol=symbol, magic=MAGIC_NUMBER)
            if not positions:
                print(f"\n[TEST SUCCESS] All {num_opened} initial positions have been successfully closed.")
                break

            print(f"--- Monitoring {len(positions)} open positions ---", end='\r')

            for pos in list(positions):
                profit = pos.profit
                if abs(profit) >= TP_SL_UNITS:
                    print(f"\n[TARGET HIT] Position #{pos.ticket} P/L is ${profit:.2f}. Closing trade.")
                    close_trade(pos)

            time.sleep(1)

    except KeyboardInterrupt:
        print("\nTest stopped by user.")
    finally:
        # --- Clean up ---
        shutdown_mt5()
        print("\n--- Test Script Finished ---")

if __name__ == "__main__":
    run_full_stress_test()