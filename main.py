import time
import MetaTrader5 as mt5
from mt5_connector import initialize_mt5, shutdown_mt5
from strategy import check_1m_strategy, check_5m_strategy
from trader import open_trade
from config import SYMBOLS, MAGIC_NUMBER

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
            # Check if there are any open positions for this symbol
            positions = mt5.positions_get(symbol=selected_symbol)
            if positions is None or len(positions) == 0:
                print("No open positions. Checking for new trade signals...")

                # --- Check for signals (5m first, then 1m) ---
                signal_5m = check_5m_strategy(selected_symbol)
                if signal_5m:
                    print(f"5m Signal found: {signal_5m}. Placing trade.")
                    open_trade(signal_5m, selected_symbol)
                else:
                    signal_1m = check_1m_strategy(selected_symbol)
                    if signal_1m:
                        print(f"1m Signal found: {signal_1m}. Placing trade.")
                        open_trade(signal_1m, selected_symbol)
                    else:
                        print("No trade signal found.")
            else:
                print(f"An open position for {selected_symbol} already exists. Waiting...")

            # --- Wait for the start of the next 1-minute candle ---
            print("Waiting for the next candle...")
            time_to_sleep = 60 - (time.time() % 60)
            time.sleep(time_to_sleep)

    except KeyboardInterrupt:
        print("\nBot stopped by user.")
    finally:
        shutdown_mt5()

if __name__ == "__main__":
    main()