from yahooquery import Ticker

from .yahooquery_cli import (calc_rev_inv_stats, get_ann_gp_margin,
                             get_ev_to_rev, get_mrq_fin_strength,
                             get_mrq_gp_margin, get_p_to_ocf, get_q_rev_growth,
                             get_ttm_ebitda_ocf, get_yearly_revenue)


def update_stock_data(stockname):
    stock = Ticker(stockname)
    fin_data = stock.financial_data[stockname]

    avg_inv_to_rev, inv_to_rev_mrq, remark_inv = calc_rev_inv_stats(stock)

    ebitda, ocf, tot_rev = get_ttm_ebitda_ocf(stock, fin_data)

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
    ev_to_rev = get_ev_to_rev(stock, key_stats)

    summary_detail = stock.summary_detail[stockname]
    p_to_ocf = get_p_to_ocf(summary_detail, ocf)

    stock_stats = {
        'symbol': stockname,
        'equity_ratio': equity_ratio * 100,
        'ndebt_to_ebitda': equity_ratio * 100,
        'net_debt_ebitda': net_debt / ebitda,
        'inv_to_rev_mrq': inv_to_rev_mrq * 100,
        'avg_inv_to_rev': avg_inv_to_rev * 100,
        'q_rev_growth_ui': q_rev_growth * 100,
        'av_rev_growth_ui': av_rev_growth * 100 - 100,
        'mrq_gp_margin_ui': mrq_gp_margin * 100, 
        'av_gp_margin_ui': av_gp_margin * 100,
        'mrq_ocf_margin_ui': mrq_ocf_margin * 100, 
        'av_ocf_margin_ui': av_ocf_margin * 100,
        'mrq_fcf_margin_ui': mrq_fcf_margin * 100, 
        'av_fcf_margin_ui': av_fcf_margin * 100,
        'as_of_date': asOfDate.strftime('%m/%y'),
        'remarks_ui': remarks,
        'ev_to_rev_ui': ev_to_rev,
        'p_to_ocf_ui': p_to_ocf
    }