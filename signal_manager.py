class SignalManager:
    """
    Manages the storage and checking of active trading levels.
    This class decouples the slow signal generation from fast price checking.
    """
    def __init__(self):
        # Using sets for efficient add/remove and to avoid duplicates
        self.levels = {
            'buy': set(),
            'sell': set()
        }
        print("Signal Manager initialized.")

    def update_levels(self, new_buy_levels=None, new_sell_levels=None):
        """
        Updates the internal sets with new levels from the strategies.
        """
        if new_buy_levels:
            self.levels['buy'].update(new_buy_levels)
        if new_sell_levels:
            self.levels['sell'].update(new_sell_levels)

        print(f"[Signal Manager] Levels updated. Total Buy Levels: {len(self.levels['buy'])}, Total Sell Levels: {len(self.levels['sell'])}")

    def check_for_signal(self, current_price, point):
        """
        Checks if the current price is touching any of the stored levels.
        Returns 'buy' or 'sell' if a level is hit, otherwise None.
        Removes the level after it's been hit to prevent re-triggering.
        """
        # A small tolerance to detect a "touch"
        tolerance = 10 * point

        # Check for buy signals (price touching a support level)
        for level in list(self.levels['buy']):
            if abs(current_price - level) < tolerance:
                print(f"[Signal Manager] BUY signal triggered at support level {level:.5f}")
                self.levels['buy'].remove(level) # Use level once
                return 'buy'

        # Check for sell signals (price touching a resistance level)
        for level in list(self.levels['sell']):
            if abs(current_price - level) < tolerance:
                print(f"[Signal Manager] SELL signal triggered at resistance level {level:.5f}")
                self.levels['sell'].remove(level) # Use level once
                return 'sell'

        return None