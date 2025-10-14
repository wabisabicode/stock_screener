import math

import yahooquery as yq

from stock_screener.constants import ASYNC, MAX_WORKERS
from stock_screener.crud import add_balance_sheet_db, update_daily_metrics_db
from stock_screener.models import ReportType, Stock
from stock_screener.utils.helpers import timer

from .fin_analysis import (calc_rev_inv_stats, get_ann_gp_margin,
                           get_avg_ann_valuation, get_curr_ttm_valuation,
                           get_div_data, get_ebitda, get_inv,
                           get_mrq_fin_strength, get_mrq_margins,
                           get_q_rev_growth, get_rev_gp_fcf, get_ttm_ebitda,
                           get_yearly_revenue)


def get_daily_metrics(stock):
    ticker = stock.ticker
    stock_yq = get_stock_from_yq(ticker)
    rev_ev_fcf_data = stock_yq.get_financial_data(
        ['EnterpriseValue', 'FreeCashFlow', 'TotalRevenue'],
        frequency='a',
        trailing=True
    )

    ev, rev, fcf, ev_to_ttm_fcf, ev_to_rev = get_curr_ttm_valuation(
        rev_ev_fcf_data)

    av_ev_to_fcf, av_ev_to_rev = get_avg_ann_valuation(rev_ev_fcf_data)

    div_fwd, payout_ratio, div_yield, av_div_5y = get_div_data(
        ticker, stock_yq.summary_detail)

    stock_dict = {
        'ticker': ticker,
        'curr_ev_to_rev': ev_to_rev,
        'avg_ev_to_rev': av_ev_to_rev,
        'curr_ev_to_fcf': ev_to_ttm_fcf,
        'avg_ev_to_fcf': av_ev_to_fcf,
        'curr_fwd_div': div_yield,
        'avg_fwd_div': av_div_5y,
    }

    update_daily_metrics_db(stock, stock_dict)


def get_fin_report(stock: Stock, report_type: ReportType) -> dict:
    ticker = stock.ticker
    stock_yq = get_stock_from_yq(ticker)

    report_type_yq = report_type.value[0].lower()

    all_fields = [
        'TotalRevenue',
        'Inventory',
        'EBITDA',
        'OperatingCashFlow',
        'CashAndCashEquivalents',
        'TotalLiabilitiesNetMinorityInterest',
        'TotalEquityGrossMinorityInterest',
        'TotalDebt',
        'FreeCashFlow',
        'GrossProfit',
    ]

    q_data = stock_yq.get_financial_data(
        all_fields, frequency=report_type_yq, trailing=False)

    equity, liab, cash, totalDebt, equity_ratio, net_debt, asOfDate = get_mrq_fin_strength(q_data)

    revenue, gross_profit, free_cash_flow = get_rev_gp_fcf(q_data)

    inventory_table = get_inv(q_data)
    if inventory_table is None or inventory_table.empty:
        inventory = 0
    else:
        inventory = inventory_table.iloc[-1]

    fin_highlights = stock_yq.financial_data[ticker]
    ebitda = get_ebitda(q_data, fin_highlights)

    fin_report_dict = {
        'ticker': ticker,
        'report_type': report_type.value,
        'end_date': asOfDate,
        'total_equity': equity,
        'total_liability': liab,
        'cash_and_equivalents': cash,
        'total_debt': totalDebt,
        'inventory': inventory,

        'revenue': revenue,
        'gross_profit': gross_profit,
        'ebitda': ebitda,

        'free_cash_flow': free_cash_flow,
    }

    add_balance_sheet_db(fin_report_dict)


@timer(message=lambda ticker: f'{ticker}'.upper())
def get_stock_from_yq(ticker):
    stock = yq.Ticker(
        ticker,
        asynchronous=ASYNC,
        max_workers=MAX_WORKERS
    )

    return stock


def update_stock_data(ticker):
    stock = get_stock_from_yq(ticker)

    all_fields = ['TotalRevenue',
                  'Inventory',
                  'EBITDA',
                  'OperatingCashFlow',
                  'CashAndCashEquivalents',
                  'TotalLiabilitiesNetMinorityInterest',
                  'TotalEquityGrossMinorityInterest',
                  'TotalDebt',
                  'FreeCashFlow',
                  'GrossProfit',
                  ]

    # Use 'TotalRevenue', 'Inventory' to calculate
    # inventory to revenue for mrq and its average over quarters.
    q_data = stock.get_financial_data(
        all_fields, frequency='q', trailing=False)
    fin_highlights = stock.financial_data[ticker]

    ttm_revenue = fin_highlights.get('totalRevenue')
    avg_inv_to_rev, inv_to_rev_mrq, remark_inv = calc_rev_inv_stats(
        q_data, ttm_revenue)

    if 'EBITDA' not in q_data or q_data['EBITDA'].iloc[-4:].isna().any():
        ebitda = get_ttm_ebitda(stock, fin_highlights)
    else:
        ebitda = q_data['EBITDA'].iloc[-4:].sum()
        # ebitda here can be nan. what to do?

    if (
        'TotalRevenue' not in q_data or
        q_data['TotalRevenue'].iloc[-4:].isna().any()
    ):
        q_rev_growth = get_q_rev_growth(fin_highlights)
    else:
        q_rev_growth = (
            q_data['TotalRevenue'].iloc[-1] /
            q_data['TotalRevenue'].iloc[0] - 1
        )

    #####

    # fields used 'CashAndCashEquivalents',
    #           'TotalLiabilitiesNetMinorityInterest',
    #           'TotalEquityGrossMinorityInterest', 'TotalDebt',
    #           'FreeCashFlow'???
    equity, liab, cash, totalDebt, equity_ratio, net_debt, asOfDate = get_mrq_fin_strength(q_data)

    fields = ['TotalRevenue']
    a_inc_stat = stock.get_financial_data(
        fields, frequency='a', trailing=False)
    av_rev_growth, remark_rev = get_yearly_revenue(stock, a_inc_stat)

    # Retrieve quarterly income statement and cash flow data
    # quartal_info = stock.income_statement(frequency='q', trailing=False)
    # quartal_info = q_data
    # quartal_cf = stock.cash_flow(frequency='q', trailing=False)
    # quartal_cf = q_data
    # Fallback to trailing data if the current quarter's data is unavailable
    # if isinstance(quartal_info, str):
    #     quartal_info = stock.income_statement(frequency='q', trailing=True)
    #     quartal_cf = stock.cash_flow(frequency='q', trailing=True)
    mrq_gp_margin, mrq_fcf_margin = get_mrq_margins(
        stock, q_data)

    # Retrieve yearly income statement and cash flow data
    a_inc_stat = stock.income_statement(frequency='a', trailing=False)
    a_cf = stock.cash_flow(frequency='a', trailing=False)
    av_gp_margin, av_fcf_margin = get_ann_gp_margin(stock, a_inc_stat, a_cf)

    remarks = remark_rev + ' ' + remark_inv

    # Get valuation on EV/Rev, EV/FCF and their 4Y averages
    a_data = stock.get_financial_data(
        ['EnterpriseValue', 'FreeCashFlow', 'TotalRevenue'],
        frequency='a',
        trailing=True
    )
    ev, rev, fcf, ev_to_ttm_fcf, ev_to_rev = get_curr_ttm_valuation(a_data)
    av_ev_to_fcf, av_ev_to_rev = get_avg_ann_valuation(a_data)

    # Get valuation on Div Yield and its 5Y average
    summary_detail = stock.summary_detail
    div_fwd, payout_ratio, div_yield, av_div_5y = get_div_data(
        ticker, summary_detail)

    stock_data = {
        'symbol': ticker,
        'equity_ratio': equity_ratio * 100,
        'net_debt_to_ebitda': net_debt / ebitda,
        'inv_to_rev_mrq': inv_to_rev_mrq * 100,
        'av_inv_to_rev': avg_inv_to_rev * 100,
        'q_rev_growth': q_rev_growth * 100,
        'av_rev_growth': av_rev_growth * 100 - 100,
        'mrq_gp_margin': mrq_gp_margin * 100,
        'av_gp_margin': av_gp_margin * 100,
        'mrq_fcf_margin': mrq_fcf_margin * 100,
        'av_fcf_margin': av_fcf_margin * 100,
        'as_of_date': asOfDate.strftime('%m/%y'),
        'remarks': remarks,
        'ev_to_rev': ev_to_rev,
        'av_ev_to_rev': av_ev_to_rev,
        'ev_to_ttm_fcf': ev_to_ttm_fcf,
        'av_ev_to_fcf': av_ev_to_fcf,
        'div_yield': div_yield,
        'av_div_5y': av_div_5y,
        'div_fwd': div_fwd,
        'payout_ratio': payout_ratio * 100,
    }

    cleaned_data = {}
    for key, value in stock_data.items():
        # Check if the value is a float and is NaN
        if isinstance(value, float) and math.isnan(value):
            # Replace NaN with None (which becomes JSON null)
            cleaned_data[key] = None
        else:
            cleaned_data[key] = value

    return cleaned_data
