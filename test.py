import time
import MetaTrader5 as mt5
from mt5_connector import initialize_mt5, shutdown_mt5
from trader import open_trade, close_trade
from config import MAGIC_NUMBER

def run_round_trip_test():
    """
    Connects to MT5 and performs a full round-trip test:
    1. Opens a trade.
    2. Immediately closes the trade.
    """
    print("--- Running Round-Trip Test Script ---")
    if not initialize_mt5():
        print("[TEST FAILED] Could not initialize MT5 connection.")
        return

    symbol = "BTCUSDm"

    # --- Step 1: Open the trade ---
    open_result = open_trade('buy', symbol)

    if open_result is None or open_result.retcode != mt5.TRADE_RETCODE_DONE:
        print("[TEST FAILED] Could not open a position to test closing.")
        shutdown_mt5()
        return

    print(f"[TEST INFO] Successfully opened position #{open_result.order}. Waiting 2 seconds before closing...")
    time.sleep(2) # Wait a moment to ensure the position is fully registered on the server

    # --- Step 2: Close the trade ---
    # Fetch the position details to pass to the close function
    positions = mt5.positions_get(symbol=symbol, magic=MAGIC_NUMBER)
    if positions is None or len(positions) == 0:
        print(f"[TEST FAILED] Could not find the newly created position for {symbol}.")
        shutdown_mt5()
        return

    position_to_close = positions[0]
    close_result = close_trade(position_to_close)

    if close_result and close_result.retcode == mt5.TRADE_RETCODE_DONE:
        print("[TEST SUCCESS] Successfully opened and closed a trade.")
    else:
        print("[TEST FAILED] The closing part of the test failed.")

    # --- Clean up ---
    shutdown_mt5()
    print("--- Test Script Finished ---")

if __name__ == "__main__":
    run_round_trip_test()