from stock_screener.extensions import db
from stock_screener.models import Stock


def update_daily_metrics_db(stock: Stock, stock_dict: dict):
    stock.update_or_create(db.session, stock_dict)
