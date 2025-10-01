import time

import pandas as pd

from ..constants import (DIV_STOCKS, GROWTH_STOCKS, REST_STOCKS, TIME_PROFILE,
                        WATCHCOMM_STOCKS, WATCHGROWTH_STOCKS, WATCHLIST_STOCKS)


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


def format_value(value, format_spec, default='  -'):
    if value is None:
        return default
    return format(value, format_spec)


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


def get_stocklist(listname):
    # Mapping input options to stock lists
    stock_options = {
        "div": DIV_STOCKS,
        "growth": GROWTH_STOCKS,
        "rest": REST_STOCKS,
        "watch": WATCHLIST_STOCKS,
        "watchgrow": WATCHGROWTH_STOCKS,
        "watchcomm": WATCHCOMM_STOCKS
    }

    return stock_options.get(listname, [listname])


def display_table_header():
    print("     \t  | debt health |   inv-to-Rev\t| Rev Growth    |"
          " Gross Margin  | Free CashFlow |"
          "\t    \t    |  Valuation\t \t \t \t      | Dividend")
    print("stock\t    eqR\tnebitda\t i/Rmrq\t aIn/R\t qRGrYoY  aRGrY "
          "  mrqGM   avGMy   mrqFCF   avFCF   mrq"
          "\t Remark \tEV/Sale\t 4YEV/Sale\tEV/FCF\t 4Y EV/FCF"
          "\t DivY \t 5YDivY\t DivFwd\t Payout")
