import time
import MetaTrader5 as mt5
from mt5_connector import initialize_mt5, shutdown_mt5, get_symbol_info
from trader import open_trade, close_trade
from config import MAGIC_NUMBER, MAX_TRADES, TP_SL_UNITS

def run_live_monitoring_test():
    """
    Connects to MT5 and performs a live monitoring test:
    1. Opens MAX_TRADES number of trades.
    2. Enters a loop to monitor and close them based on TP/SL in account currency.
    3. The test completes when all initial trades have been closed.
    """
    print(f"--- Running Live Monitoring Test Script (Target: {MAX_TRADES} trades) ---")
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

    # --- Step 2: Verify trades are open ---
    initial_positions = mt5.positions_get(symbol=symbol, magic=MAGIC_NUMBER)
    if initial_positions is None or len(initial_positions) != MAX_TRADES:
        print(f"[TEST FAILED] Expected {MAX_TRADES} trades, but found {len(initial_positions or [])}. Aborting.")
        shutdown_mt5()
        return

    print(f"Successfully opened {len(initial_positions)} trades. Entering live monitoring mode...")
    print(f"This test will run until all positions are closed by hitting the +/- ${TP_SL_UNITS} target.")

    # --- Step 3: Monitor until all trades are closed ---
    try:
        while True:
            positions = mt5.positions_get(symbol=symbol, magic=MAGIC_NUMBER)
            if positions is None:
                print("Could not get position data. Retrying...")
                time.sleep(1)
                continue

            # Exit condition for the test
            if len(positions) == 0:
                print("[TEST SUCCESS] All initial positions have been successfully closed.")
                break

            print(f"--- Monitoring {len(positions)} open positions ---")

            for pos in list(positions):
                # Use pos.profit to get P/L directly in account currency
                profit_in_currency = pos.profit

                print(f"[MONITOR] Position #{pos.ticket}, P/L: ${profit_in_currency:.2f}")

                if profit_in_currency >= TP_SL_UNITS or profit_in_currency <= -TP_SL_UNITS:
                    print(f"[TARGET HIT] Position #{pos.ticket} P/L is ${profit_in_currency:.2f}. Closing trade.")
                    close_trade(pos)

            time.sleep(1) # Loop every second for active monitoring

    except KeyboardInterrupt:
        print("\nTest stopped by user.")
    finally:
        # --- Clean up ---
        shutdown_mt5()
        print("--- Test Script Finished ---")

if __name__ == "__main__":
    run_live_monitoring_test()