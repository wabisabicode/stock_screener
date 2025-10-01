import json

from stock_screener.crud import update_stock_data
from stock_screener.utils.helpers import get_stocklist


def format_sse(data: dict) -> str:
    return f'data: {json.dumps(data)}\n\n'


def generate_stock_updates(tickers: str):
    stocks_list = get_stocklist(tickers)

    for stockname in stocks_list:
        try:
            # Skip any intentionally blank tickers in your lists
            if not stockname:
                yield format_sse({})
                continue  # Go to the next item in the loop

            # Attempt to process the stock data
            print(f"Processing {stockname}...")
            updated_data = update_stock_data(stockname)
            yield format_sse(updated_data)

        except Exception as e:
            print(f'!!! ERROR processing {stockname}: {e}')

            # Create an error object to send to the browser
            error_data = {
                "symbol": stockname,
                "remarks": 'Failed to process. See server console for error.',
                "error": True  # Add a flag for JavaScript
            }
            yield format_sse(error_data)

    yield 'data: [DONE]\n\n'
