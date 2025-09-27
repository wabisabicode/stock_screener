import yahooquery as yq

from .constants import ASYNC, MAX_WORKERS
from .utils import timer


def get_stock_fin_report():
    ...


@timer(message=lambda ticker: f'{ticker}'.upper())
def get_stock_from_yq(ticker):
    stock = yq.Ticker(
        ticker,
        asynchronous=ASYNC,
        max_workers=MAX_WORKERS
    )

    return stock
