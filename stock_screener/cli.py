import click
from flask.cli import with_appcontext

from stock_screener.models import Stock, db


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
