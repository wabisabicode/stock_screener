import time

import click
from flask.cli import with_appcontext

from stock_screener.models import ReportType, Stock, db
from stock_screener.yfinance_api import get_daily_metrics, get_fin_report


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
    stocks = [stock for stock in Stock.query.all()]

    print('Starting update of the daily metrics')
    updated_daily_count = 0
    failed_tickers = []

    for stock in stocks:
        try:
            get_daily_metrics(stock)
            # check end_date. if new report is available:
            # get_fin_report(ticker, ReportType.QUARTERLY)
            print(f'Successfully updated {stock}')
            updated_daily_count += 1
        except Exception as e:
            print(f"!!! FAILED to update {stock}: {e}")
            failed_tickers.append(stock)

    time.sleep(1)

    print("\n----- Update Complete -----")
    print(f'Daily metrics updated: {updated_daily_count}/{len(tickers)}')
    if failed_tickers:
        print(f"Failed tickers: {', '.join(failed_tickers)}")
