import time

import click
from flask.cli import with_appcontext

from stock_screener.models import Stock, db
from stock_screener.services import get_stock_fin_report


@click.command('add-tickers')
@click.argument('tickers_list')
@with_appcontext
def add_tickers_command(tickers_list):

    tickers = [t.strip().upper() for t in tickers_list.split(',')]

    for ticker in tickers:
        if not Stock.query.filter_by(ticker=ticker).first():
            stock = Stock(ticker=ticker)
            db.session.add(stock)
            print(f'Added ticker {ticker}')

    db.session.commit()
    print('Adding stocks completed.')


@click.command('update-stocks')
@with_appcontext
def update_stocks():
    tickers = [stock.ticker for stock in Stock.query.all()]

    print('Starting update of the stocks')
    updated_count = 0
    failed_tickers = []

    for ticker in tickers:
        try:
            get_stock_fin_report(ticker)
            print(f'Successfully updated {ticker}')
            updated_count += 1
        except Exception as e:
            print(f"!!! FAILED to update {ticker}: {e}")
            failed_tickers.append(ticker)

    time.sleep(1)

    print("\n----- Update Complete -----")
    print(f"Successfully updated: {updated_count}/{len(tickers)}")
    if failed_tickers:
        print(f"Failed tickers: {', '.join(failed_tickers)}")
