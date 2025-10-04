import time
import MetaTrader5 as mt5
from mt5_connector import initialize_mt5, shutdown_mt5, get_symbol_info
from strategy import check_1m_strategy, check_5m_strategy
from trader import open_trade, close_trade
from config import SYMBOLS, MAGIC_NUMBER, TP_SL_UNITS

def main():
    """
    Main function to run the trading bot.
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
    print(f"Trading {selected_symbol}...")
    print("Bot is running. Press Ctrl+C to stop.")

    # --- Main trading loop ---
    try:
        while True:
            # Check for open positions managed by this bot
            positions = mt5.positions_get(symbol=selected_symbol, magic=MAGIC_NUMBER)
            if positions is None:
                print("Could not get position data. Retrying...")
                time.sleep(1)
                continue

            if len(positions) > 0:
                # --- MONITORING MODE ---
                position = positions[0]
                point = get_symbol_info(selected_symbol).point

                # Determine current price for P/L calculation
                if position.type == mt5.ORDER_TYPE_BUY:
                    current_price = mt5.symbol_info_tick(selected_symbol).bid
                    profit_in_points = (current_price - position.price_open) / point
                else: # position.type == mt5.ORDER_TYPE_SELL
                    current_price = mt5.symbol_info_tick(selected_symbol).ask
                    profit_in_points = (position.price_open - current_price) / point

                print(f"[MONITOR] Position #{position.ticket}, P/L: {profit_in_points:.2f} points")

                # Check for TP/SL conditions
                if profit_in_points >= TP_SL_UNITS:
                    print(f"[TP HIT] Profit of {profit_in_points:.2f} points reached target of {TP_SL_UNITS}. Closing trade.")
                    close_trade(position)
                elif profit_in_points <= -TP_SL_UNITS:
                    print(f"[SL HIT] Loss of {profit_in_points:.2f} points reached target of -{TP_SL_UNITS}. Closing trade.")
                    close_trade(position)

                time.sleep(1) # Check P/L every second

            else:
                # --- SEARCHING MODE ---
                print("No open positions. Checking for new trade signals...")
                signal_5m = check_5m_strategy(selected_symbol)
                if signal_5m:
                    open_trade(signal_5m, selected_symbol)
                else:
                    signal_1m = check_1m_strategy(selected_symbol)
                    if signal_1m:
                        open_trade(signal_1m, selected_symbol)
                    else:
                        print("No trade signal found.")

                print("Waiting for the next candle...")
                time_to_sleep = 60 - (time.time() % 60)
                time.sleep(time_to_sleep)

    except KeyboardInterrupt:
        print("\nBot stopped by user.")
    finally:
        shutdown_mt5()

if __name__ == "__main__":
    main()