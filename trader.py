import MetaTrader5 as mt5
from config import MAGIC_NUMBER, LOT_SIZE
from mt5_connector import get_symbol_info

def has_sufficient_margin(action, symbol, lot_size):
    """
    Checks if the account has enough free margin to open a trade.
    """
    # Get account margin information
    account_info = mt5.account_info()
    if account_info is None:
        print("Failed to get account info.")
        return False

    free_margin = account_info.margin_free

    # Get the current price, which is required for margin calculation
    price = mt5.symbol_info_tick(symbol).ask if action == 'buy' else mt5.symbol_info_tick(symbol).bid

    # Calculate required margin for the trade
    request = {
        "action": mt5.ORDER_TYPE_BUY if action == 'buy' else mt5.ORDER_TYPE_SELL,
        "symbol": symbol,
        "volume": lot_size,
        "price": price,
    }

    required_margin = mt5.order_calc_margin(request['action'], symbol, lot_size, price)

    if required_margin is None:
        print(f"order_calc_margin failed, error code = {mt5.last_error()}")
        return False

    print(f"Margin Check: Required=${required_margin:.2f}, Available=${free_margin:.2f}")

    if free_margin >= required_margin:
        return True
    else:
        return False

def open_trade(action, symbol):
    """
    Opens a trade with the specified action ('buy' or 'sell')
    after verifying sufficient margin.
    """
    print(f"Attempting to open a {action} trade for {symbol}...")

    # --- 1. Pre-trade margin check ---
    if not has_sufficient_margin(action, symbol, LOT_SIZE):
        print(f"Trade failed: Not enough free margin to open a {LOT_SIZE} lot trade on {symbol}.")
        return None # Indicate failure due to margin

    # --- 2. Open the trade if margin is sufficient ---
    price = mt5.symbol_info_tick(symbol).ask if action == 'buy' else mt5.symbol_info_tick(symbol).bid
    trade_type = mt5.ORDER_TYPE_BUY if action == 'buy' else mt5.ORDER_TYPE_SELL

    print(f"Trade Details: Lot={LOT_SIZE}, Price={price:.5f}")

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": LOT_SIZE,
        "type": trade_type,
        "price": price,
        "sl": 0.0,
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

    if position.type == mt5.ORDER_TYPE_BUY:
        close_type = mt5.ORDER_TYPE_SELL
        price = mt5.symbol_info_tick(symbol).bid
    else:
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