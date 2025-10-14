from stock_screener.extensions import db
from stock_screener.models import Stock, FinancialReport


def update_daily_metrics_db(stock: Stock, stock_dict: dict):
    stock.update_or_create(db.session, stock_dict)


def add_balance_sheet_db(data):
    ticker = data.pop('ticker')

    stock = db.session.query(Stock).filter_by(ticker=ticker).first()

    try:
        new_fin_report = FinancialReport(**data)
        stock.reports.append(new_fin_report)
        db.session.commit()
        print(f'New fin_report for {ticker} added successfully.')
    except Exception as e:
        db.session.rollback()
        print(f'Failed to add report for {stock.ticker}: {e}')
