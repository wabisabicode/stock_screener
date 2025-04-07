from datetime import datetime

from yahooquery import Ticker

from .utils import (calc_rev_inv_stats, elapsed_time, get_ann_gp_margin,
                    get_ev_to_rev, get_mrq_fin_strength, get_mrq_gp_margin,
                    get_p_to_ocf, get_q_rev_growth, get_ttm_ebitda_ocf,
                    get_yearly_revenue, timer)


@timer
def update_stock_data(stockname):
    time_start_anal = datetime.now()

    stock = Ticker(stockname, asynchronous=False)
    time_got_ticker = elapsed_time(time_start_anal, 'Got ticker in')
    fin_data = stock.financial_data[stockname]
    time_got_fin_data = elapsed_time(time_got_ticker, 'Got fin_data in')

    # revenue has to be summed up
    fields_tosum = ['TotalRevenue', 'Inventory']
    tosum_info = stock.get_financial_data(
        fields_tosum, frequency='q', trailing=False)
    avg_inv_to_rev, inv_to_rev_mrq, remark_inv = calc_rev_inv_stats(stock, tosum_info)

    quartal_cf = stock.cash_flow(frequency='q', trailing=True)
    ebitda, ocf, tot_rev = get_ttm_ebitda_ocf(stock, fin_data, quartal_cf)

    equity_ratio, net_debt, asOfDate = get_mrq_fin_strength(stock)

    q_rev_growth = get_q_rev_growth(fin_data)
    av_rev_growth, remark_rev = get_yearly_revenue(stock)

    mrq_gp_margin, mrq_ocf_margin, mrq_fcf_margin = get_mrq_gp_margin(stock)

    av_gp_margin, av_ocf_margin, av_fcf_margin = get_ann_gp_margin(stock)

    remarks = remark_rev + ' ' + remark_inv

    # get current valuations for EV-to-Rev and Price/OCF
    if stockname != 'bion.sw':
        key_stats = stock.key_stats[stockname]
    else:
        key_stats = 0

    valuation_measures = stock.valuation_measures
    ev_to_rev = get_ev_to_rev(key_stats, valuation_measures)

    p_to_ocf = get_p_to_ocf(valuation_measures, ocf)

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
        'mrq_ocf_margin': mrq_ocf_margin * 100,
        'av_ocf_margin': av_ocf_margin * 100,
        'mrq_fcf_margin': mrq_fcf_margin * 100,
        'av_fcf_margin': av_fcf_margin * 100,
        'as_of_date': asOfDate.strftime('%m/%y'),
        'remarks': remarks,
        'ev_to_rev': ev_to_rev,
        'p_to_ocf': p_to_ocf
    }

    return stock_data
