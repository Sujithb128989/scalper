import MetaTrader5 as mt5
from mt5_connector import initialize_mt5, shutdown_mt5, get_symbol_info
from config import MAGIC_NUMBER, FALLBACK_STOP_DISTANCE_UNITS

def run_test_trade():
    """
    Connects to MT5 and places a single test trade. It uses the broker's
    minimum stop distance, with a configurable fallback if the broker reports zero.
    """
    print("--- Running Test Script ---")
    if not initialize_mt5():
        print("[TEST FAILED] Could not initialize MT5 connection.")
        return

    symbol = "BTCUSDm"
    print(f"Attempting to place a test 'buy' trade for {symbol}...")

    symbol_info = get_symbol_info(symbol)
    if symbol_info is None:
        print(f"[TEST FAILED] Could not get symbol info for {symbol}.")
        shutdown_mt5()
        return

    # --- Determine a valid stop distance for the test trade ---
    lot_size = symbol_info.volume_min
    price = mt5.symbol_info_tick(symbol).ask
    point = symbol_info.point
    broker_min_stops = symbol_info.trade_stops_level

    print(f"Broker's minimum stop distance for {symbol}: {broker_min_stops} points.")

    # Safeguard: If broker reports 0, use our configurable fallback value.
    if broker_min_stops == 0:
        distance_for_test = FALLBACK_STOP_DISTANCE_UNITS
        print(f"Broker reported 0, using configured fallback distance of {distance_for_test} points.")
    else:
        distance_for_test = broker_min_stops

    # Set TP/SL using the determined valid distance
    tp = price + distance_for_test * point
    sl = price - distance_for_test * point

    print(f"Test trade details: Price={price:.5f}, TP={tp:.5f}, SL={sl:.5f}, Lot={lot_size}")

    # --- Prepare and send the trade request ---
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot_size,
        "type": mt5.ORDER_TYPE_BUY,
        "price": price,
        "sl": sl,
        "tp": tp,
        "magic": MAGIC_NUMBER,
        "comment": "test script trade",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(request)

    # --- Check result ---
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"[TEST FAILED] Order send failed. Retcode={result.retcode}, Comment={result.comment}")
    else:
        print(f"[TEST SUCCESS] Order successfully sent. Order ID: {result.order}")

    # --- Clean up ---
    shutdown_mt5()
    print("--- Test Script Finished ---")

if __name__ == "__main__":
    run_test_trade()