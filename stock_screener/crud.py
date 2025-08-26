from datetime import datetime

#from yahooquery import Ticker
import yahooquery as yq

from .utils import (calc_rev_inv_stats, elapsed_time, get_ann_gp_margin,
                    get_div_data, get_mrq_fin_strength,
                    get_mrq_margins, get_valuation, get_q_rev_growth,
                    get_ttm_ebitda, get_yearly_revenue, timer)


@timer
def update_stock_data(ticker):
    time_start_anal = datetime.now()

    stock = yq.Ticker(ticker, asynchronous=True)
    time_got_ticker = elapsed_time(time_start_anal, f'Got {ticker} in')

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
    q_data = stock.get_financial_data(all_fields, frequency='q', trailing=False)
    fin_highlights = stock.financial_data[ticker]

    print(type(fin_highlights))

    ttm_revenue = fin_highlights.get('totalRevenue')
    avg_inv_to_rev, inv_to_rev_mrq, remark_inv = calc_rev_inv_stats(q_data, ttm_revenue)

    if 'EBITDA' not in q_data or q_data['EBITDA'].iloc[-4:].isna().any():
        ebitda = get_ttm_ebitda(stock, fin_highlights)
    else:
        ebitda = q_data['EBITDA'].iloc[-4:].sum()
        # ebitda here can be nan. what to do?

    if 'TotalRevenue' not in q_data or q_data['TotalRevenue'].iloc[-4:].isna().any():
        q_rev_growth = get_q_rev_growth(fin_highlights)
    else:
        q_rev_growth = q_data['TotalRevenue'].iloc[-1] / q_data['TotalRevenue'].iloc[0] - 1

    #####

    # fields used 'CashAndCashEquivalents',
    #           'TotalLiabilitiesNetMinorityInterest',
    #           'TotalEquityGrossMinorityInterest', 'TotalDebt',
    #           'FreeCashFlow'???
    equity_ratio, net_debt, asOfDate = get_mrq_fin_strength(stock, q_data)

    fields = ['TotalRevenue']
    a_inc_stat = stock.get_financial_data(fields, frequency='a', trailing=False)
    av_rev_growth, remark_rev = get_yearly_revenue(stock, a_inc_stat)

    # Retrieve quarterly income statement and cash flow data
    # quartal_info = stock.income_statement(frequency='q', trailing=False)
    quartal_info = q_data
    # quartal_cf = stock.cash_flow(frequency='q', trailing=False)
    quartal_cf = q_data
    # Fallback to trailing data if the current quarter's data is unavailable
    # if isinstance(quartal_info, str):
    #     quartal_info = stock.income_statement(frequency='q', trailing=True)
    #     quartal_cf = stock.cash_flow(frequency='q', trailing=True)
    mrq_gp_margin, mrq_fcf_margin = get_mrq_margins(stock, quartal_info, quartal_cf)

    # Retrieve yearly income statement and cash flow data
    a_inc_stat = stock.income_statement(frequency='a', trailing=False)
    a_cf = stock.cash_flow(frequency='a', trailing=False)
    av_gp_margin, av_fcf_margin = get_ann_gp_margin(stock, a_inc_stat, a_cf)

    remarks = remark_rev + ' ' + remark_inv

    # Get valuation on EV/Rev, EV/FCF and their 4Y averages
    a_data = stock.get_financial_data(['EnterpriseValue', 'FreeCashFlow', 'TotalRevenue'], frequency='a', trailing=True)
    ev_to_ttm_fcf, av_ev_to_fcf, ev_to_rev, av_ev_to_rev = get_valuation(stock, a_data)

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
        'payout_ratio': payout_ratio,
    }

    return stock_data
