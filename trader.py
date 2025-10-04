import MetaTrader5 as mt5
from config import TP_SL_UNITS, MAGIC_NUMBER
from mt5_connector import get_symbol_info

def open_trade(action, symbol):
    """
    Opens a trade with the specified action ('buy' or 'sell').
    Lot size is dynamically fetched based on the minimum allowed volume.

    Args:
        action (str): The trade direction, 'buy' or 'sell'.
        symbol (str): The symbol to trade.

    Returns:
        The result of the order_send operation.
    """
    print(f"Attempting to open a {action} trade for {symbol}...")

    symbol_info = get_symbol_info(symbol)
    if symbol_info is None:
        print(f"Trade failed: Could not get symbol info for {symbol}.")
        return None

    # Dynamically fetch the minimum lot size
    lot_size = symbol_info.volume_min
    print(f"Using minimum lot size: {lot_size}")

    # Determine the correct price based on the action
    price = mt5.symbol_info_tick(symbol).ask if action == 'buy' else mt5.symbol_info_tick(symbol).bid
    point = symbol_info.point

    # Set SL and TP based on a fixed unit distance from the entry price
    if action == 'buy':
        trade_type = mt5.ORDER_TYPE_BUY
        sl = price - TP_SL_UNITS * point
        tp = price + TP_SL_UNITS * point
    elif action == 'sell':
        trade_type = mt5.ORDER_TYPE_SELL
        sl = price + TP_SL_UNITS * point
        tp = price - TP_SL_UNITS * point
    else:
        print(f"Invalid action: {action}")
        return None

    print(f"Price: {price}, SL: {sl}, TP: {tp}")

    # Build the trade request
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

    # Send the trade request
    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Order send failed, retcode={result.retcode}, comment={result.comment}")
    else:
        print(f"Order successfully sent, position #{result.order}")

    return result