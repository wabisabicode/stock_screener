import json
import time

from flask import (Blueprint, Response, redirect, render_template, request,
                   url_for)

from .crud import update_stock_data
from .yahooquery_cli import form_stock_list

main = Blueprint('main', __name__)


@main.route('/update')
def update_universe():
    pass


@main.route('/')
def home():
    return render_template('home.html')


@main.route('/results', methods=['GET', 'POST'])
def results():
    """
    This endpoint handles both the form submission (POST)
    and displaying the results page (GET).
    """
    if request.method == 'POST':
        stock_key = request.form.get('stock_key')
        custom_ticker = request.form.get('custom_ticker')

        if stock_key == 'custom' and custom_ticker:
            tickers_to_process = custom_ticker
        else:
            tickers_to_process = stock_key

        # Redirect to this SAME URL, but as a GET request
        return redirect(url_for('main.results', tickers=tickers_to_process))

    # This block runs after the redirect, when the browser makes a GET request
    # to a URL like "/results?tickers=AAPL,GOOGL". Its only job is to
    # show the blank results page so the JavaScript can take over.
    return render_template('results.html')


@main.route('/stream-results')
def stream_results():
    stock_from_ui = request.args.get('tickers', '')
    stocks_list = form_stock_list(stock_from_ui)

    def generate():
        for stockname in stocks_list:
            try:
                # Skip any intentionally blank tickers in your lists
                if not stockname:
                    yield f'data: {json.dumps({})}\n\n'
                    continue  # Go to the next item in the loop

                # Attempt to process the stock data
                print(f"Processing {stockname}...")
                updated_data = update_stock_data(stockname)
                yield f'data: {json.dumps(updated_data)}\n\n'

            except Exception as e:
                print(f'!!! ERROR processing {stockname}: {e}')

                # Create an error object to send to the browser
                error_data = {
                    "symbol": stockname,
                    "remarks": 'Failed to process. See server console for error.',
                    "error": True  # Add a flag for JavaScript
                }
                yield f'data: {json.dumps(error_data)}\n\n'

        yield 'data: [DONE]\n\n'

    return Response(generate(), mimetype='text/event-stream')
