import time

import pandas as pd

from .constants import TIME_PROFILE


# Function to safely extract the last non-null value from a series
def get_last_value(data, key, default=0):
    try:
        return data[key].dropna().iloc[-1]
    except (KeyError, ValueError, IndexError):
        return default


# Function to safely extract a non-null table
def get_non_null_table(data, key):
    try:
        return data[key].dropna()
    except (KeyError, ValueError):
        return pd.Series(dtype=float)


def timer(message=None):
    def decorator(func):
        """A decorator that prints the time a function takes to execute."""
        def wrapper(*args, **kwargs):
            if TIME_PROFILE:
                start_time = time.perf_counter()
                result = func(*args, **kwargs)
                run_time = time.perf_counter() - start_time

                if callable(message):
                    msg = message(*args, **kwargs)
                    print('')
                    print(f'Getting ticker {msg} took {run_time:.4f} seconds')
                else:
                    print(f'{func.__name__} took {run_time:.4f} seconds')

                return result
            else:
                return func(*args, **kwargs)

        return wrapper
    return decorator
