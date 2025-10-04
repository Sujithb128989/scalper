import MetaTrader5 as mt5
from config import TP_SL_UNITS, MAGIC_NUMBER
from mt5_connector import get_symbol_info

def open_trade(action, symbol):
    """
    Opens a trade with the specified action ('buy' or 'sell').
    Dynamically adjusts SL/TP to meet broker's minimum stop level.
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

    # --- Ensure SL/TP distance meets broker's minimum requirement ---
    stops_level = symbol_info.trade_stops_level
    distance_units = TP_SL_UNITS

    if distance_units < stops_level:
        print(f"[WARNING] Configured TP/SL of {distance_units} units is less than broker's minimum of {stops_level} units.")
        print(f"Adjusting to use the broker's minimum distance.")
        distance_units = stops_level

    # --- Set SL and TP based on the adjusted distance ---
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