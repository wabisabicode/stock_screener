from datetime import datetime

# Function to safely extract the last non-null value from a series
def get_last_value(data, key, default=0):
    try:
        return data[key].dropna().iloc[-1]
    except (KeyError, ValueError, IndexError):
        return default


# Function to safely extract a non-null table
def get_non_null_table(data, key, default=0):
    try:
        return data[key].dropna()
    except (KeyError, ValueError):
        return default


# Time profiling
def elapsed_time(time_start, message):
    time_now = datetime.now()
    print(f'{message}: {time_now - time_start}')
    return time_now
