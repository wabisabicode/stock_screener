from datetime import datetime

from yahooquery import Ticker

from .utils import (calc_rev_inv_stats, elapsed_time, get_ann_gp_margin,
                    get_ev_to_rev, get_mrq_fin_strength, get_mrq_margins,
                    get_q_rev_growth, get_ttm_ebitda, get_yearly_revenue,
                    timer)


@timer
def update_stock_data(stockname):
    time_start_anal = datetime.now()

    stock = Ticker(stockname, asynchronous=False)
    time_got_ticker = elapsed_time(time_start_anal, 'Got ticker in')

    all_fields = ['TotalRevenue',
                  'Inventory',
                  'EBITDA',
                  'OperatingCashFlow',
                  'CashAndCashEquivalents',
                  'TotalLiabilitiesNetMinorityInterest',
                  'TotalEquityGrossMinorityInterest',
                  'TotalDebt',
                  'OperatingCashFlow',
                  'FreeCashFlow',
                  'GrossProfit',
                  ]

    # fields used 'TotalRevenue', 'Inventory'
    q_data = stock.get_financial_data(all_fields, frequency='q', trailing=False)
    avg_inv_to_rev, inv_to_rev_mrq, remark_inv = calc_rev_inv_stats(stock, q_data)

    # was:
    # quartal_cf = stock.cash_flow(frequency='q', trailing=True)
    # ebitda, ocf, tot_rev = get_ttm_ebitda_ocf(stock, fin_data, quartal_cf)
    # uses 'ebitda', 'operatingCashflow', 'totalRevenue' - can be done with get_financial_data()
    # q_rev_growth = get_q_rev_growth(fin_data)  # uses 'revenueGrowth'

    # now:
    # fields used 'EBITDA', 'TotalRevenue'

    fin_highlights = stock.financial_data[stockname]
    if 'EBITDA' not in q_data:
        ebitda = get_ttm_ebitda(stock, fin_highlights)
    else:
        ebitda = q_data['EBITDA'].iloc[-4:].sum()

    if 'TotalRevenue' not in q_data:
        q_rev_growth = get_q_rev_growth(fin_highlights)
    else:
        q_rev_growth = q_data['TotalRevenue'].iloc[-1] / q_data['TotalRevenue'].iloc[0] - 1

    #####

    # fields used 'CashAndCashEquivalents',
    #           'TotalLiabilitiesNetMinorityInterest',
    #           'TotalEquityGrossMinorityInterest', 'TotalDebt',
    #           'OperatingCashFlow', 'FreeCashFlow'
    equity_ratio, net_debt, asOfDate = get_mrq_fin_strength(stock, q_data)

    fields = ['TotalRevenue']
    yearly_info = stock.get_financial_data(
        fields, frequency='a', trailing=False)
    av_rev_growth, remark_rev = get_yearly_revenue(stock, yearly_info)

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
    yearly_info = stock.income_statement(frequency='a', trailing=False)
    yearly_cf = stock.cash_flow(frequency='a', trailing=False)
    av_gp_margin, av_fcf_margin = get_ann_gp_margin(stock, yearly_info, yearly_cf)

    remarks = remark_rev + ' ' + remark_inv

    # get current valuations for EV-to-Rev and Price/OCF
    if stockname != 'bion.sw':
        key_stats = stock.key_stats[stockname]
    else:
        key_stats = 0

    valuation_measures = stock.valuation_measures
    ev_to_rev = get_ev_to_rev(key_stats, valuation_measures)

    # p_to_ocf = get_p_to_ocf(valuation_measures, ocf)

    stock_data = {
        'symbol': stockname,
        'equity_ratio': equity_ratio * 100,
        'net_debt_to_ebitda': net_debt / ebitda,
        'inv_to_rev_mrq': inv_to_rev_mrq * 100,
        'av_inv_to_rev': avg_inv_to_rev * 100,
        'q_rev_growth': q_rev_growth * 100,
        'av_rev_growth': av_rev_growth * 100 - 100,
        'mrq_gp_margin': mrq_gp_margin * 100,
        'av_gp_margin': av_gp_margin * 100,
        # 'mrq_ocf_margin': mrq_ocf_margin * 100,
        # 'av_ocf_margin': av_ocf_margin * 100,
        'mrq_fcf_margin': mrq_fcf_margin * 100,
        'av_fcf_margin': av_fcf_margin * 100,
        'as_of_date': asOfDate.strftime('%m/%y'),
        'remarks': remarks,
        'ev_to_rev': ev_to_rev,
        # 'p_to_ocf': p_to_ocf
    }

    return stock_data
