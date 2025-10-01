import time

import click
from flask.cli import with_appcontext

from stock_screener.crud import update_stock_data
from stock_screener.extensions import db
from stock_screener.models import ReportType, Stock
from stock_screener.services.yfinance_api import (get_daily_metrics,
                                                  get_fin_report)
from stock_screener.utils.helpers import (display_table_header, format_value,
                                          get_stocklist)


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
    print(f'Daily metrics updated: {updated_daily_count}/{len(stocks)}')
    if failed_tickers:
        print(f"Failed tickers: {', '.join(failed_tickers)}")


@click.group('stocks')
def stocks_cli():
    pass


@stocks_cli.command('update')
@click.argument('ticker')
@with_appcontext
def update_command(ticker):
    display_table_header()
    stocks_list = get_stocklist(ticker)

    for stockname in stocks_list:
        if stockname != '':
            stock_data = update_stock_data(stockname)

            print(
                f'{format_value(stockname, "10s")}',
                f'{format_value(stock_data["equity_ratio"], "4.0f")}%',
                f'{format_value(stock_data["net_debt_to_ebitda"], "5.1f")} \t',
                f'{format_value(stock_data["inv_to_rev_mrq"], "3.0f")}% \t',
                f'{format_value(stock_data["av_inv_to_rev"], "3.0f")}% \t',
                f'{format_value(stock_data["q_rev_growth"], "3.0f")}% \t',
                f'{format_value(stock_data["av_rev_growth"], "3.0f")}% \t',
                f'{format_value(stock_data["mrq_gp_margin"], "4.0f")}% \t',
                f'{format_value(stock_data["av_gp_margin"], "4.0f")}% \t',
                f'{format_value(stock_data["mrq_fcf_margin"], "4.0f")}% \t',
                f'{format_value(stock_data["av_fcf_margin"], "4.0f")}% \t',
                f'{format_value(stock_data["as_of_date"], "")}',
                f'{format_value(stock_data["remarks"], "")} \t',
                f'{format_value(stock_data["ev_to_rev"], "4.1f")} \t  ',
                f'{format_value(stock_data["av_ev_to_rev"], "4.1f", "   -  ")} \t',
                f'{format_value(stock_data["ev_to_ttm_fcf"], "5.1f", "   -  ")}\t ',
                f'{format_value(stock_data["av_ev_to_fcf"], "4.1f")} \t \t',
                f'{format_value(stock_data["div_yield"], "3.1f")} \t',
                f'{format_value(stock_data["av_div_5y"], "3.1f")} \t',
                f'{format_value(stock_data["div_fwd"], "6.2f")}\t',
                f'{format_value(stock_data["payout_ratio"], "5.1f")}',
            )
        else:
            print(' ')
