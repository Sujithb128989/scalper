import MetaTrader5 as mt5
from config import TP_SL_UNITS, MAGIC_NUMBER, FALLBACK_STOP_DISTANCE_UNITS
from mt5_connector import get_symbol_info

def open_trade(action, symbol):
    """
    Opens a trade with the specified action ('buy' or 'sell').
    Dynamically adjusts SL/TP to meet broker's minimum stop level,
    with a configurable fallback for invalid broker data.
    """
    print(f"Attempting to open a {action} trade for {symbol}...")

    symbol_info = get_symbol_info(symbol)
    if symbol_info is None:
        print(f"Trade failed: Could not get symbol info for {symbol}.")
        return None

    # --- Dynamically fetch instrument settings ---
    lot_size = symbol_info.volume_min
    point = symbol_info.point
    price = mt5.symbol_info_tick(symbol).ask if action == 'buy' else mt5.symbol_info_tick(symbol).bid

    # --- Determine a valid stop distance ---
    distance_units = TP_SL_UNITS
    broker_min_stops = symbol_info.trade_stops_level

    # Determine the effective minimum distance: use broker's if valid, else our fallback.
    if broker_min_stops > 0:
        effective_min_distance = broker_min_stops
    else:
        print(f"[WARNING] Broker reported an invalid minimum stop level of {broker_min_stops}. Using configured fallback of {FALLBACK_STOP_DISTANCE_UNITS} points.")
        effective_min_distance = FALLBACK_STOP_DISTANCE_UNITS

    # Ensure our desired distance meets the effective minimum.
    if distance_units < effective_min_distance:
        print(f"[WARNING] Configured TP/SL of {distance_units} units is less than the effective minimum of {effective_min_distance} units.")
        print(f"Adjusting to use the effective minimum distance.")
        distance_units = effective_min_distance

    # --- Set SL and TP based on the final, valid distance ---
    if action == 'buy':
        trade_type = mt5.ORDER_TYPE_BUY
        sl = price - distance_units * point
        tp = price + distance_units * point
    elif action == 'sell':
        trade_type = mt5.ORDER_TYPE_SELL
        sl = price + distance_units * point
        tp = price - distance_units * point
    else:
        print(f"Invalid action: {action}")
        return None

    print(f"Trade Details: Lot={lot_size}, Price={price:.5f}, SL={sl:.5f}, TP={tp:.5f}")

    # --- Build and send the trade request ---
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot_size,
        "type": trade_type,
        "price": price,
        "sl": sl,
        "tp": tp,
        "magic": MAGIC_NUMBER,
        "comment": "python bot",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Order send failed, retcode={result.retcode}, comment={result.comment}")
    else:
        print(f"Order successfully sent, position #{result.order}")

    return result