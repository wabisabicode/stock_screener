# Function to safely extract the last non-null value from a series
def get_last_value(data, key):
    try:
        return data[key].dropna().iloc[-1]
    except (KeyError, ValueError, IndexError):
        return 0.
