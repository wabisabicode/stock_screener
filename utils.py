# Function to safely extract the last non-null value from a series
def get_last_value(data, key):
    try:
        return data[key].dropna().iloc[-1]
    except (KeyError, ValueError, IndexError):
        return 0.


# Function to safely extract a non-null table
def get_non_null_table(data, key, default=0):
    try:
        return data[key].dropna()
    except (KeyError, ValueError):
        return default
