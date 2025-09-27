from flask import (Blueprint, Response, redirect, render_template, request,
                   url_for)

from .streaming import generate_stock_updates

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

        # Redirect to SAME URL, but as a GET "/results?tickers=AAPL,GOOGL".
        return redirect(url_for('main.results', tickers=tickers_to_process))

    return render_template('results.html')


@main.route('/stream-results')
def stream_results():
    tickers = request.args.get('tickers', '')
    return Response(generate_stock_updates(tickers), mimetype='text/event-stream')
