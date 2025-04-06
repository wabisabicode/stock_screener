from datetime import datetime

from yahooquery import Ticker

from .utils import (calc_rev_inv_stats, elapsed_time, get_ann_gp_margin,
                    get_ev_to_rev, get_mrq_fin_strength, get_mrq_gp_margin,
                    get_p_to_ocf, get_q_rev_growth, get_ttm_ebitda_ocf,
                    get_yearly_revenue)


def update_stock_data(stockname):
    time_start_anal = datetime.now()

    stock = Ticker(stockname, asynchronous=False)
    time_got_ticker = elapsed_time(time_start_anal, 'Got ticker in')
    fin_data = stock.financial_data[stockname]
    time_got_fin_data = elapsed_time(time_got_ticker, 'Got fin_data in')

    avg_inv_to_rev, inv_to_rev_mrq, remark_inv = calc_rev_inv_stats(stock)
    time_calc_rev_inv = elapsed_time(time_got_fin_data, 'Calc rev inv in')

    ebitda, ocf, tot_rev = get_ttm_ebitda_ocf(stock, fin_data)
    time_got_ttm_ebitda_ocf = elapsed_time(time_calc_rev_inv, 'Got ebitda, ocf in')

    equity_ratio, net_debt, asOfDate = get_mrq_fin_strength(stock)
    time_got_fin_strength = elapsed_time(time_got_ttm_ebitda_ocf, 'Got fin strength in')

    q_rev_growth = get_q_rev_growth(fin_data)
    av_rev_growth, remark_rev = get_yearly_revenue(stock)
    time_got_rev_growth = elapsed_time(time_got_fin_strength, 'Got rev growth in')

    mrq_gp_margin, mrq_ocf_margin, mrq_fcf_margin = get_mrq_gp_margin(stock)
    time_got_mrq_margins = elapsed_time(time_got_rev_growth, 'Got mrq margins in')

    av_gp_margin, av_ocf_margin, av_fcf_margin = get_ann_gp_margin(stock)
    time_got_av_margins = elapsed_time(time_got_mrq_margins, 'Got av margins in')

    remarks = remark_rev + ' ' + remark_inv

    # get current valuations for EV-to-Rev and Price/OCF
    if stockname != 'bion.sw':
        key_stats = stock.key_stats[stockname]
    else:
        key_stats = 0

    ev_to_rev = get_ev_to_rev(stock, key_stats)

    summary_detail = stock.summary_detail[stockname]
    p_to_ocf = get_p_to_ocf(summary_detail, ocf)

    time_got_valuations = elapsed_time(time_got_av_margins, 'Got valuations in')
    print('------')
    time_total = elapsed_time(time_start_anal, 'Got stock done in')
    print('')

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
