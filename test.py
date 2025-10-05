import time
import MetaTrader5 as mt5
from mt5_connector import initialize_mt5, shutdown_mt5, get_symbol_info
from trader import open_trade, close_trade
from signal_manager import SignalManager
from strategy import find_fractal_levels_5m, find_qualified_fvg_levels_1m
from config import MAGIC_NUMBER, TP_SL_UNITS, LOT_SIZES

def run_end_to_end_test():
    """
    Connects to MT5 and performs a full, end-to-end integration test:
    1. Populates the SignalManager with initial levels.
    2. Waits for a price level to be hit and opens ONE trade.
    3. Monitors that trade's P/L until the target is hit.
    4. Closes the trade and confirms success.
    """
    print(f"--- Running Full End-to-End Test Script ---")
    if not initialize_mt5():
        print("[TEST FAILED] Could not initialize MT5 connection.")
        return

    symbol = "BTCUSDm"
    signal_manager = SignalManager()

    # --- Step 1: Populate Signal Manager with initial levels ---
    print("\n--- Populating Signal Manager with initial levels... ---")
    s_levels, r_levels = find_fractal_levels_5m(symbol)
    signal_manager.update_levels({lvl: 'buy' for lvl in s_levels})
    signal_manager.update_levels({lvl: 'sell' for lvl in r_levels})

    fvg_buy_levels, fvg_sell_levels = find_qualified_fvg_levels_1m(symbol)
    signal_manager.update_levels({lvl: 'buy' for lvl in fvg_buy_levels})
    signal_manager.update_levels({lvl: 'sell' for lvl in fvg_sell_levels})

    if not signal_manager.levels:
        print("[TEST SKIPPED] No initial trade levels found. Cannot perform live test.")
        shutdown_mt5()
        return

    print(f"\n--- Entering Live Monitoring Mode. Waiting for a level to be hit... ---")

    trade_opened = False
    try:
        while True:
            # --- Step 2 & 3: Wait for a signal and open ONE trade ---
            if not trade_opened:
                price = mt5.symbol_info_tick(symbol).bid
                point = get_symbol_info(symbol).point
                signal = signal_manager.check_for_signal(price, point)

                if signal:
                    print(f"\n--- Level Hit! Opening one '{signal}' trade to test management. ---")
                    result = open_trade(signal, symbol)
                    if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                        trade_opened = True
                        print("\n--- Trade Opened. Now monitoring P/L until target is hit... ---")
                    else:
                        print("[TEST FAILED] Failed to open trade after signal was triggered.")
                        break

            # --- Step 4 & 5: Monitor the single open trade and close on target ---
            if trade_opened:
                positions = mt5.positions_get(symbol=symbol, magic=MAGIC_NUMBER)
                if not positions:
                    print("[TEST SUCCESS] Position was successfully closed by the P/L logic.")
                    break

                position = positions[0]
                profit = position.profit
                print(f"[MONITOR] Position #{position.ticket}, P/L: ${profit:.2f}", end='\r')

                if abs(profit) >= TP_SL_UNITS:
                    print(f"\n[TARGET HIT] Position #{position.ticket} P/L is ${profit:.2f}. Closing trade.")
                    close_trade(position)
                    time.sleep(2) # Give time for server to confirm close

            time.sleep(1)

    except KeyboardInterrupt:
        print("\nTest stopped by user.")
    finally:
        # --- Clean up ---
        shutdown_mt5()
        print("--- Test Script Finished ---")

if __name__ == "__main__":
    run_end_to_end_test()