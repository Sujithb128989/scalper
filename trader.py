import MetaTrader5 as mt5
from config import MAGIC_NUMBER
from mt5_connector import get_symbol_info

def open_trade(action, symbol):
    """
    Opens a trade with the specified action ('buy' or 'sell')
    without setting SL or TP levels.
    """
    print(f"Attempting to open a {action} trade for {symbol}...")

    symbol_info = get_symbol_info(symbol)
    if symbol_info is None:
        print(f"Trade failed: Could not get symbol info for {symbol}.")
        return None

    lot_size = symbol_info.volume_min
    price = mt5.symbol_info_tick(symbol).ask if action == 'buy' else mt5.symbol_info_tick(symbol).bid
    trade_type = mt5.ORDER_TYPE_BUY if action == 'buy' else mt5.ORDER_TYPE_SELL

    print(f"Trade Details: Lot={lot_size}, Price={price:.5f}")

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot_size,
        "type": trade_type,
        "price": price,
        "sl": 0.0,  # SL/TP are not set at trade opening
        "tp": 0.0,
        "magic": MAGIC_NUMBER,
        "comment": "python bot open",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Order send failed, retcode={result.retcode}, comment={result.comment}")
    else:
        print(f"Order successfully sent, position #{result.order}")

    return result

def close_trade(position):
    """
    Closes the given position at the current market price.
    """
    symbol = position.symbol

    # Determine the closing order type and price
    if position.type == mt5.ORDER_TYPE_BUY:
        close_type = mt5.ORDER_TYPE_SELL
        price = mt5.symbol_info_tick(symbol).bid
    else: # position.type == mt5.ORDER_TYPE_SELL
        close_type = mt5.ORDER_TYPE_BUY
        price = mt5.symbol_info_tick(symbol).ask

    print(f"Attempting to close position #{position.ticket} for {symbol} at price {price:.5f}...")

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": position.volume,
        "type": close_type,
        "position": position.ticket,
        "price": price,
        "magic": MAGIC_NUMBER,
        "comment": "python bot close",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Close order failed, retcode={result.retcode}, comment={result.comment}")
    else:
        print(f"Position #{position.ticket} successfully closed.")

    return result