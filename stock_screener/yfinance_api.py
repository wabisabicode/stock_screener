import yahooquery as yq

from .constants import ASYNC, MAX_WORKERS
from .utils import timer, get_curr_ttm_valuation


def get_daily_metrics(stock):
    rev_ev_fcf_data = stock.get_financial_data(
        ['EnterpriseValue', 'FreeCashFlow', 'TotalRevenue'],
        frequency='a',
        trailing=True
    )
    ev, rev, fcf, ev_to_ttm_fcf, ev_to_rev = get_curr_ttm_valuation(stock, rev_ev_fcf_data)


def get_fin_report(stock, report_type):
    ...


@timer(message=lambda ticker: f'{ticker}'.upper())
def get_stock_from_yq(ticker):
    stock = yq.Ticker(
        ticker,
        asynchronous=ASYNC,
        max_workers=MAX_WORKERS
    )

    return stock
