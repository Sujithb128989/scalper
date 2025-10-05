import time
import MetaTrader5 as mt5
from mt5_connector import initialize_mt5, shutdown_mt5, get_symbol_info
from trader import open_trade, close_trade
from config import MAGIC_NUMBER, MAX_TRADES, TP_SL_UNITS, LOT_SIZES

def run_live_monitoring_test():
    """
    Connects to MT5 and performs a robust live monitoring test using
    the per-symbol lot size configuration.
    """
    print(f"--- Running Robust Live Monitoring Test Script ---")
    if not initialize_mt5():
        print("[TEST FAILED] Could not initialize MT5 connection.")
        return

    symbol = "BTCUSDm"
    lot_size = LOT_SIZES.get(symbol)
    if not lot_size:
        print(f"[TEST FAILED] No lot size configured for symbol '{symbol}' in config.py.")
        shutdown_mt5()
        return

    # --- Step 1: Attempt to open trades ---
    print(f"Attempting to open up to {MAX_TRADES} trades of {lot_size} lots each for {symbol}...")
    for i in range(MAX_TRADES):
        print(f"Attempting to open trade {i + 1}/{MAX_TRADES}...")
        open_trade('buy', symbol)
        time.sleep(0.2)

    # --- Step 2: Verify at least one trade is open ---
    initial_positions = mt5.positions_get(symbol=symbol, magic=MAGIC_NUMBER)
    num_opened = len(initial_positions or [])

    if num_opened == 0:
        print("[TEST FAILED] Could not open a single trade. Please check account margin or logs.")
        shutdown_mt5()
        return

    print(f"Successfully opened {num_opened} trades. Entering live monitoring mode...")
    print(f"This test will run until all {num_opened} positions are closed by hitting the +/- ${TP_SL_UNITS} target.")

    # --- Step 3: Monitor until all trades are closed ---
    try:
        while True:
            positions = mt5.positions_get(symbol=symbol, magic=MAGIC_NUMBER)
            if positions is None:
                print("Could not get position data. Retrying...")
                time.sleep(1)
                continue

            if len(positions) == 0:
                print(f"[TEST SUCCESS] All {num_opened} initial positions have been successfully closed.")
                break

            print(f"--- Monitoring {len(positions)} open positions ---")

            for pos in list(positions):
                profit_in_currency = pos.profit
                print(f"[MONITOR] Position #{pos.ticket}, P/L: ${profit_in_currency:.2f}")

                if abs(profit_in_currency) >= TP_SL_UNITS:
                    print(f"[TARGET HIT] Position #{pos.ticket} P/L is ${profit_in_currency:.2f}. Closing trade.")
                    close_trade(pos)

            time.sleep(1)

    except KeyboardInterrupt:
        print("\nTest stopped by user.")
    finally:
        # --- Clean up ---
        shutdown_mt5()
        print("--- Test Script Finished ---")

if __name__ == "__main__":
    run_live_monitoring_test()