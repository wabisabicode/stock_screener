import enum
from sqlalchemy import Enum

from . import db


class ReportType(enum.Enum):
    QUARTERLY = 'QUARTERLY'
    ANNUAL = 'ANNUAL'


class StockData(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Unique identifier
    ticker = db.Column(db.String(10), nullable=False)  # Stock ticker like 'O'

    equity_ratio = db.Column(db.Float)  # Equity ratio as a percentage
    ndebt_to_ebitda = db.Column(db.Float)  # Debt to EBITDA ratio
    net_debt_ebitda = db.Column(db.Float)  # Net debt to EBITDA ratio

    inv_to_rev_mrq = db.Column(db.Float)  # Inventory to revenue (mrq)
    avg_inv_to_rev = db.Column(db.Float)  # Average inventory to revenue

    q_rev_growth = db.Column(db.Float)  # Quarterly revenue growth
    av_rev_growth = db.Column(db.Float)  # Annual revenue growth
    mrq_gp_margin = db.Column(db.Float)  # Gross profit margin (mrq)
    av_gp_margin = db.Column(db.Float)  # Average gross profit margin

    mrq_ocf_margin = db.Column(db.Float)  # Operating cash flow margin (mrq)
    av_ocf_margin = db.Column(db.Float)  # Average operating cash flow margin
    mrq_fcf_margin = db.Column(db.Float)  # Free cash flow margin (mrq)
    av_fcf_margin = db.Column(db.Float)  # Average free cash flow margin

    as_of_date = db.Column(db.String(5))  # Date in 'MM/YY' format
    remarks = db.Column(db.String(50))  # Additional remarks

    ev_to_rev = db.Column(db.Float)  # EV to revenue
    p_to_ocf = db.Column(db.Float)  # Price to operating cash flow

    @staticmethod
    def update_or_create(session, stock_dict):
        ticker = stock_dict.get('ticker')

        if not ticker:
            raise ValueError(
                'The stock dictionary must contain the "ticker" key.')

        stock = session.query(StockData).filter_by(ticker=ticker).first()

        if stock:
            for key, value in stock_dict.items():
                if hasattr(stock, key):
                    setattr(stock, key, value)

            session.commit()
            print(f'Stock {ticker} updated successfully.')
        else:
            print(
                f'Stock with ticker {ticker} not found. Adding a new record.')
            new_stock = StockData(**stock_dict)
            session.add(new_stock)
            session.commit()
            print(f'New stock {ticker} added successfully.')
