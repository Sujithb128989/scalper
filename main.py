import time
import MetaTrader5 as mt5
from mt5_connector import initialize_mt5, shutdown_mt5, get_symbol_info
from strategy import find_fractal_levels_5m, find_qualified_fvg_levels_1m
from trader import open_trade, close_trade
from signal_manager import SignalManager
from config import SYMBOLS, MAGIC_NUMBER, TP_SL_UNITS, MAX_TRADES

def main():
    """
    Main function to run the bot with the new, efficient, event-driven architecture.
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
    print(f"TP/SL target is set to ${TP_SL_UNITS} per trade.")
    print("Bot is running. Press Ctrl+C to stop.")

    # --- Initialize Signal Manager and Timers ---
    signal_manager = SignalManager()
    last_5m_scan_time = 0
    last_1m_scan_time = 0

    try:
        while True:
            current_time = time.time()

            # --- LOW-FREQUENCY TASKS (Signal Generation) ---
            # Scan for 5m fractal levels every 5 minutes
            if current_time - last_5m_scan_time >= 300:
                print("\n--- Scanning for 5m Support/Resistance levels... ---")
                supports, resistances = find_fractal_levels_5m(selected_symbol)
                signal_manager.update_levels(new_buy_levels=supports, new_sell_levels=resistances)
                last_5m_scan_time = current_time

            # Scan for 1m FVG levels every 1 minute
            if current_time - last_1m_scan_time >= 60:
                print("\n--- Scanning for 1m FVG levels... ---")
                buy_levels, sell_levels = find_qualified_fvg_levels_1m(selected_symbol)
                signal_manager.update_levels(new_buy_levels=buy_levels, new_sell_levels=sell_levels)
                last_1m_scan_time = current_time

            # --- HIGH-FREQUENCY TASKS (Trade Management & Execution) ---
            # 1. Manage existing positions
            positions = mt5.positions_get(symbol=selected_symbol, magic=MAGIC_NUMBER)
            if positions:
                for pos in list(positions):
                    profit = pos.profit
                    print(f"[MONITOR] Position #{pos.ticket}, P/L: ${profit:.2f}", end='\r')
                    if abs(profit) >= TP_SL_UNITS:
                        print(f"\n[TARGET HIT] Position #{pos.ticket} P/L is ${profit:.2f}. Closing trade.")
                        close_trade(pos)

            # 2. Check for new trade entries
            num_open_trades = len(positions or [])
            if num_open_trades < MAX_TRADES:
                price = mt5.symbol_info_tick(selected_symbol).bid # Use bid for checking both S/R
                point = get_symbol_info(selected_symbol).point
                signal = signal_manager.check_for_signal(price, point)

                if signal:
                    print(f"\n[EXECUTION] Found {signal} signal from Signal Manager. Attempting to open trade.")
                    open_trade(signal, selected_symbol)

            time.sleep(1)

    except KeyboardInterrupt:
        print("\nBot stopped by user.")
    finally:
        shutdown_mt5()

if __name__ == "__main__":
    main()