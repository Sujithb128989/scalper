import time
import MetaTrader5 as mt5
from mt5_connector import initialize_mt5, shutdown_mt5
from trader import open_trade, close_trade
from config import MAGIC_NUMBER, MAX_TRADES

def run_multi_trade_test():
    """
    Connects to MT5 and performs a multi-trade stress test:
    1. Opens the MAX_TRADES number of trades.
    2. Verifies they are all open.
    3. Closes all of them.
    """
    print(f"--- Running Multi-Trade Test Script (Target: {MAX_TRADES} trades) ---")
    if not initialize_mt5():
        print("[TEST FAILED] Could not initialize MT5 connection.")
        return

    symbol = "BTCUSDm"

    # --- Step 1: Open all trades ---
    print(f"Attempting to open {MAX_TRADES} trades...")
    for i in range(MAX_TRADES):
        print(f"Opening trade {i + 1}/{MAX_TRADES}...")
        open_trade('buy', symbol)
        time.sleep(0.2) # Small delay between requests

    # --- Step 2: Verify all trades are open ---
    positions = mt5.positions_get(symbol=symbol, magic=MAGIC_NUMBER)
    if positions is None:
        print("[TEST FAILED] Could not retrieve positions from server.")
        shutdown_mt5()
        return

    num_opened = len(positions)
    print(f"Verification: {num_opened}/{MAX_TRADES} trades were successfully opened.")
    if num_opened == 0:
        print("[TEST FAILED] No trades were opened.")
        shutdown_mt5()
        return

    # --- Step 3: Close all open trades ---
    print(f"Attempting to close all {num_opened} open trades...")
    # We convert to a list because closing a position modifies the collection we are iterating over
    for pos in list(positions):
        close_trade(pos)
        time.sleep(0.2) # Small delay between requests

    # --- Step 4: Final Verification ---
    final_positions = mt5.positions_get(symbol=symbol, magic=MAGIC_NUMBER)
    if final_positions is None or len(final_positions) == 0:
        print(f"[TEST SUCCESS] Successfully opened {num_opened} trades and closed them all.")
    else:
        print(f"[TEST FAILED] {len(final_positions)} trades remain open after attempting to close all.")

    # --- Clean up ---
    shutdown_mt5()
    print("--- Test Script Finished ---")

if __name__ == "__main__":
    run_multi_trade_test()