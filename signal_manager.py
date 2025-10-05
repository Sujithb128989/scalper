class SignalManager:
    """
    Manages the storage and checking of active trading levels using a
    more efficient key-value structure as designed by the user.
    """
    def __init__(self):
        # A single dictionary where: {price_level: 'buy'/'sell'}
        self.levels = {}
        print("Signal Manager initialized with new key-value structure.")

    def update_levels(self, new_levels_dict):
        """
        Updates the internal dictionary with new levels from the strategies.
        new_levels_dict should be in the format {level: type}.
        """
        if new_levels_dict:
            self.levels.update(new_levels_dict)

        print(f"[Signal Manager] Levels updated. Total active levels: {len(self.levels)}")

    def check_for_signal(self, current_price, point):
        """
        Checks if the current price is touching any of the stored levels.
        Returns the trade type ('buy' or 'sell') if a level is hit, otherwise None.
        Removes the level after it's been hit to prevent re-triggering.
        """
        tolerance = 10 * point
        level_to_trade = None
        trade_type = None

        for level, t_type in self.levels.items():
            if abs(current_price - level) < tolerance:
                print(f"[Signal Manager] {t_type.upper()} signal triggered at level {level:.5f}")
                level_to_trade = level
                trade_type = t_type
                break # Found a level, stop checking

        # Remove the level outside the loop to avoid modifying dict while iterating
        if level_to_trade:
            del self.levels[level_to_trade]
            return trade_type

        return None