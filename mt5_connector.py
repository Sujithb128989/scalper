import MetaTrader5 as mt5

def initialize_mt5():
    """Initializes the connection to the MetaTrader 5 terminal."""
    if not mt5.initialize():
        print(f"initialize() failed, error code = {mt5.last_error()}")
        return False
    print("MT5 connection initialized successfully.")
    return True

def shutdown_mt5():
    """Shuts down the connection to the MetaTrader 5 terminal."""
    mt5.shutdown()
    print("MT5 connection shut down.")

def get_symbol_info(symbol):
    """Fetches symbol information and selects it in MarketWatch."""
    # Ensure symbol is available in MarketWatch
    if not mt5.symbol_select(symbol, True):
        print(f"Failed to select {symbol} in MarketWatch, error code = {mt5.last_error()}")
        # We can still try to get info, maybe it's already selected

    info = mt5.symbol_info(symbol)
    if info is None:
        print(f"Failed to get symbol info for {symbol}, error code = {mt5.last_error()}")

    return info

def get_market_data(symbol, timeframe, count):
    """Fetches market data for a given symbol and timeframe."""
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
    if rates is None or len(rates) == 0:
        print(f"Failed to get rates for {symbol}/{timeframe}, error code = {mt5.last_error()}")
        return None
    return rates