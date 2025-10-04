import time
import MetaTrader5 as mt5
from mt5_connector import initialize_mt5, shutdown_mt5, get_symbol_info
from strategy import check_1m_strategy, check_5m_strategy
from trader import open_trade, close_trade
from config import SYMBOLS, MAGIC_NUMBER, TP_SL_UNITS, MAX_TRADES

def main():
    """
    Main function to run the multi-trade trading bot.
    """
    if not initialize_mt5():
        return

    # --- User selects instrument ---
    print("Please select the instrument to trade:")
    for key, value in SYMBOLS.items():
        print(f"{key}: {value}")

    selected_key = ""
    while selected_key not in SYMBOLS:
        selected_key = input("Enter the number for the symbol: ").strip()
        if selected_key not in SYMBOLS:
            print("Invalid selection. Please choose a valid number.")

    selected_symbol = SYMBOLS[selected_key]
    print(f"Trading {selected_symbol} with up to {MAX_TRADES} simultaneous trades...")
    print("Bot is running. Press Ctrl+C to stop.")

    # --- Main trading loop ---
    try:
        while True:
            # --- 1. Monitor all open positions ---
            positions = mt5.positions_get(symbol=selected_symbol, magic=MAGIC_NUMBER)
            if positions is None:
                print("Could not get position data. Retrying...")
                time.sleep(1)
                continue

            if len(positions) > 0:
                point = get_symbol_info(selected_symbol).point
                for pos in list(positions):
                    if pos.type == mt5.ORDER_TYPE_BUY:
                        current_price = mt5.symbol_info_tick(selected_symbol).bid
                        profit_in_points = (current_price - pos.price_open) / point
                    else: # pos.type == mt5.ORDER_TYPE_SELL
                        current_price = mt5.symbol_info_tick(selected_symbol).ask
                        profit_in_points = (pos.price_open - current_price) / point

                    print(f"[MONITOR] Position #{pos.ticket}, P/L: {profit_in_points:.2f} points")

                    if profit_in_points >= TP_SL_UNITS or profit_in_points <= -TP_SL_UNITS:
                        print(f"[TARGET HIT] Position #{pos.ticket} P/L is {profit_in_points:.2f}. Closing trade.")
                        close_trade(pos)

            # --- 2. Check for new trade opportunities ---
            # Re-fetch positions to get the most current count after potential closing
            num_open_trades = len(mt5.positions_get(symbol=selected_symbol, magic=MAGIC_NUMBER))
            print(f"Bot status: {num_open_trades}/{MAX_TRADES} open positions.")

            if num_open_trades < MAX_TRADES:
                print("Checking for new trade signals...")
                signal_5m = check_5m_strategy(selected_symbol)
                if signal_5m:
                    print(f"[SIGNAL] 5m signal found: {signal_5m}. Opening new trade.")
                    open_trade(signal_5m, selected_symbol)
                else:
                    signal_1m = check_1m_strategy(selected_symbol)
                    if signal_1m:
                        print(f"[SIGNAL] 1m signal found: {signal_1m}. Opening new trade.")
                        open_trade(signal_1m, selected_symbol)
                    else:
                        print("No trade signal found.")
            else:
                print("Position limit reached. Not checking for new signals.")

            time.sleep(1) # Loop every second for active monitoring

    except KeyboardInterrupt:
        print("\nBot stopped by user.")
    finally:
        shutdown_mt5()

if __name__ == "__main__":
    main()