import enum

from sqlalchemy import Enum

from stock_screener import db


class ReportType(enum.Enum):
    QUARTERLY = 'QUARTERLY'
    ANNUAL = 'ANNUAL'


class Stock(db.Model):
    # Never change:
    id = db.Column(db.Integer, primary_key=True)  # Unique identifier
    ticker = db.Column(db.String(10), nullable=False,
                       unique=True, index=True)  # Stock ticker like 'O'

    reports = db.relationship(
        'FinancialReport', backref='stock',
        lazy='dynamic', cascade="all, delete-orphan")

    # Calculated once per quarter from the new FinancialReport
    curr_equity_ratio = db.Column(db.Float)  # Equity ratio as a percentage
    curr_net_debt_to_ebitda = db.Column(db.Float)  # Net Debt to EBITDA ratio

    mrq_inv_to_rev = db.Column(db.Float)  # Inventory to revenue (mrq)
    avg_inv_to_rev = db.Column(db.Float)  # Average inventory to revenue

    mrq_yoy_rev_growth = db.Column(db.Float)  # Quarterly revenue growth
    avg_rev_growth = db.Column(db.Float)  # Annual revenue growth
    mrq_gp_margin = db.Column(db.Float)  # Gross profit margin (mrq)
    avg_gp_margin = db.Column(db.Float)  # Average gross profit margin
    mrq_fcf_margin = db.Column(db.Float)  # Free cash flow margin (mrq)
    avg_fcf_margin = db.Column(db.Float)  # Average free cash flow margin

    curr_div_rate_rev = db.Column(db.Float)  # Current dividend in (Eur, $)

    curr_end_date = db.Column(db.Date)  # Date in 'MM/YY' format
    remarks = db.Column(db.String(50))  # Additional remarks

    # Calculated daily:
    curr_ev_to_rev = db.Column(db.Float)  # EV to revenue
    avg_ev_to_rev = db.Column(db.Float)  # 5Y average EV to revenue
    curr_fcf_to_rev = db.Column(db.Float)  # FCF to revenue
    avg_fcf_to_rev = db.Column(db.Float)  # 5Y average FCF to revenue

    curr_fwd_div = db.Column(db.Float)  # current forward yield
    avg_fwd_div = db.Column(db.Float)  # 5Y average forward yield

    @staticmethod
    def update_or_create(session, stock_dict):
        ticker = stock_dict.get('ticker')

        if not ticker:
            raise ValueError(
                'The stock dictionary must contain the "ticker" key.')

        stock = session.query(Stock).filter_by(ticker=ticker).first()

        if stock:
            for key, value in stock_dict.items():
                if hasattr(stock, key):
                    setattr(stock, key, value)

            session.commit()
            print(f'Stock {ticker} updated successfully.')
        else:
            print(
                f'Stock with ticker {ticker} not found. Adding a new record.')
            new_stock = Stock(**stock_dict)
            session.add(new_stock)
            session.commit()
            print(f'New stock {ticker} added successfully.')


class FinancialReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    stock_id = db.Column(db.Integer, db.ForeignKey('stock.id'),
                         nullable=False, index=True)

    # --- Report Metadata ---
    report_type = db.Column(Enum(ReportType), nullable=False)
    end_date = db.Column(db.Date, nullable=False)

    # --- Balance Sheet Data ---
    total_equity = db.Column(db.BigInteger)
    total_liability = db.Column(db.BigInteger)
    cash_and_equivalents = db.Column(db.BigInteger)
    total_debt = db.Column(db.BigInteger)
    inventory = db.Column(db.BigInteger)

    # --- Income Statement Data ---
    revenue = db.Column(db.BigInteger)
    gross_profit = db.Column(db.BigInteger)
    ebitda = db.Column(db.BigInteger)

    # --- Cash Flow Statement Data ---
    free_cash_flow = db.Column(db.BigInteger)
