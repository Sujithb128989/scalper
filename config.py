# --- MT5 Account Credentials ---
# Please fill in your account details below.
# You can find these details in your MT5 terminal under File -> Login to Trade Account
MT5_ACCOUNT = 259303309  # Replace with your account number
MT5_PASSWORD = "ReyRey192!"  # Replace with your password
MT5_SERVER = "Exness-MT5Trial15"  # Replace with your server name (e.g., Exness-MT5Real7)

# --- Trading Configuration ---
# Symbols are mapped to a simple number for easy selection.
SYMBOLS = {
    "1": "BTCUSDm",
    "2": "XAUUSD"
}

# --- Stop Loss and Take Profit ---
# The distance in points for your Stop Loss and Take Profit.
# This will be used to programmatically close the trade.
TP_SL_UNITS = 50

# --- Other Settings ---
MAGIC_NUMBER = 12345