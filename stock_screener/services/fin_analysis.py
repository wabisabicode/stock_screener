import numpy as np
import pandas as pd

from stock_screener.utils.helpers import (get_last_value, get_non_null_table,
                                          timer)


# ----------------------------------------------
# get ttm ebitda from asset profile
# ----------------------------------------------
@timer()
def get_ttm_ebitda(_stock, _fin_data):
    try:
        ebitda = _fin_data.get('ebitda', 0.)
    except AttributeError:
        ebitda = 0.

    return ebitda


@timer()
def get_q_rev_growth(_fin_data):
    """Get year-over-year revenue growth for the most recent quarter."""

    try:
        _q_rev_growth = _fin_data['revenueGrowth']
    except (KeyError, ValueError):
        _q_rev_growth = float('nan')

    # Check if _q_rev_growth is an (empty) dict and set to 0 if so
    if isinstance(_q_rev_growth, dict):
        _q_rev_growth = 0.

    return _q_rev_growth


# ----------------------------------------------
# get gross profit margin of the mrq (or ttm)
# ----------------------------------------------
@timer()
def get_mrq_margins(_stock, quartal_info, quartal_cf):
    """
    Get the most recent quarter's gross profit margin,
    operating cash flow margin, and free cash flow margin.
    """
    # Extract financial metrics
    gp = get_last_value(quartal_info, 'GrossProfit')
    fcf = get_last_value(quartal_cf, 'FreeCashFlow')
    rev = get_last_value(quartal_info, 'TotalRevenue')

    # Calculate margins
    gp_margin = gp / rev if gp > 0 and rev > 0 else float('nan')
    fcf_margin = fcf / rev if rev > 0 else float('nan')

    return gp_margin, fcf_margin


# ----------------------------------------------
# get gross profit margin of the mrq (or ttm)
# ----------------------------------------------
@timer()
def get_ann_gp_margin(_stock, a_inc_stat, a_cf):
    """
    Get annual gross profit margin, operating cash flow margin,
    and free cash flow margin.
    """
    # Extract financial tables
    gps = get_non_null_table(a_inc_stat, 'GrossProfit')
    fcfs = get_non_null_table(a_cf, 'FreeCashFlow')
    totrevs = get_non_null_table(a_inc_stat, 'TotalRevenue')

    totrevs_len = totrevs.size

    # calculate rev growth rates via annual revenues
    if not gps.empty:
        gp_margin = [gps.iloc[i] / totrevs.iloc[i]
                     for i in range(totrevs_len)]
        gp_margin = np.average(gp_margin)
    else:
        no_totexp = False
        try:
            totexps = a_inc_stat['TotalExpenses']
        except KeyError:
            totexps = totrevs  # no gp margin and no total expenses
            no_totexp = True

        gp_margin = [totrevs.iloc[i] - totexps.iloc[i] / totrevs.iloc[i]
                     for i in range(totrevs_len)]
        gp_margin = np.average(gp_margin)
        if no_totexp:
            gp_margin = float('nan')

    # calculate free cashflow margin for latest years
    if not fcfs.empty:
        try:
            fcf_margin = [fcfs.iloc[i] / totrevs.iloc[i]
                          for i in range(totrevs_len)]
            fcf_margin = np.average(fcf_margin)
        except IndexError:
            pass
    else:
        fcf_margin = float('nan')

    return gp_margin, fcf_margin


# ----------------------------------------------
# get ttm ebitda from asset profile
# ----------------------------------------------
@timer()
def get_mrq_fin_strength(_stock, quartal_info):

    cash = get_last_value(quartal_info, 'CashAndCashEquivalents')
    liab = get_last_value(quartal_info, 'TotalLiabilitiesNetMinorityInterest')
    equity = get_last_value(quartal_info, 'TotalEquityGrossMinorityInterest')
    totalDebt = get_last_value(quartal_info, 'TotalDebt', float('nan'))

    _asOfDate = get_last_value(quartal_info, 'asOfDate')
    _equity_ratio = equity / (equity + liab)
    _net_debt = totalDebt - cash

    return _equity_ratio, _net_debt, _asOfDate


@timer()
def get_yearly_revenue(_stock, a_info):
    """ get annual revenues, calculate growth rates
    and pass average rev growth of passed years"""
    if type(a_info) is not str:
        num_years = a_info.shape[0]
    else:
        num_years = 0

    revs = a_info['TotalRevenue'].iloc[:]
    # print(yearly_info['TotalRevenue'])
    # calculate rev growth rates via annual revenues
    r_growth = []

    for i in range(len(revs) - 1, 0, -1):
        r_growth.append(revs.iloc[i]/revs.iloc[i-1])

    _r_growth_tot = np.prod(r_growth)

    if (_r_growth_tot > 0.):
        _av_rev_growth = np.prod(r_growth) ** (1./(num_years - 1))
    else:
        _av_rev_growth = float('nan')

    _remark_rev = str(num_years) + 'Yrev'

    return _av_rev_growth, _remark_rev


@timer()
def calc_rev_inv_stats(q_data, ttm_revenue):
    q_inv = get_non_null_table(q_data, 'Inventory')

    inv_quarter_count = len(q_inv)
    remark = 'inv' + str(inv_quarter_count) + 'Q'

    # calculate mrq and average inventory to ttm revenue
    if inv_quarter_count > 0 and ttm_revenue and not np.isnan(ttm_revenue):
        mrq_inv = q_inv.iloc[-1]
        mrq_inv_to_rev = mrq_inv / ttm_revenue
        av_inv_to_rev = np.average(q_inv) / ttm_revenue
    else:
        av_inv_to_rev = mrq_inv_to_rev = float('nan')

    return av_inv_to_rev, mrq_inv_to_rev, remark


@timer()
def get_div_data(stockname, summary_detail):
    summary_detail = summary_detail.get(stockname, {})  # unpack the outer dict

    div_fwd = summary_detail.get('dividendRate')
    payout_ratio = summary_detail.get('payoutRatio')
    div_yield = summary_detail.get('dividendYield')
    av_div_5y = summary_detail.get('fiveYearAvgDividendYield')

    div_yield = div_yield * 100 if div_yield is not None else None

    return div_fwd, payout_ratio, div_yield, av_div_5y


@timer()
def get_curr_ttm_valuation(stockname, a_fcf_ev):
    ttm_data = a_fcf_ev[a_fcf_ev['periodType'] == 'TTM']

    ev = get_last_value(ttm_data, 'EnterpriseValue', float('nan'))
    rev = get_last_value(ttm_data, 'TotalRevenue', float('nan'))
    fcf = get_last_value(ttm_data, 'FreeCashFlow', float('nan'))

    # actually, rev and fcf are not updated daily
    ev_to_rev = ev / rev
    ev_to_ttm_fcf = ev / fcf

    return ev, rev, fcf, ev_to_ttm_fcf, ev_to_rev


@timer()
def get_avg_ann_valuation(stockname, a_fcf_ev):
    a_data = a_fcf_ev[a_fcf_ev['periodType'] == '12M']

    evs = a_data.get('EnterpriseValue', pd.Series(dtype=float))
    revs = a_data.get('TotalRevenue', pd.Series(dtype=float))
    fcfs = a_data.get('FreeCashFlow', pd.Series(dtype=float))

    av_ev_to_rev = (evs / revs).dropna().mean()
    av_ev_to_fcf = (evs / fcfs).dropna().mean()

    return av_ev_to_fcf, av_ev_to_rev
