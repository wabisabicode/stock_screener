import numpy as np
import pandas as pd

from .helpers import get_last_value, get_non_null_table, timer


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
    _mrq_gp = get_last_value(quartal_info, 'GrossProfit')
    _mrq_fcf = get_last_value(quartal_cf, 'FreeCashFlow')
    _mrq_rev = get_last_value(quartal_info, 'TotalRevenue')

    # Calculate margins
    _mrq_gp_margin = _mrq_gp / _mrq_rev if _mrq_gp > 0 and _mrq_rev > 0 else float('nan')
    _mrq_fcf_margin = _mrq_fcf / _mrq_rev if _mrq_rev > 0 else float('nan')

    return _mrq_gp_margin, _mrq_fcf_margin


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
    _gp_table = get_non_null_table(a_inc_stat, 'GrossProfit')
    _fcf_table = get_non_null_table(a_cf, 'FreeCashFlow')
    _totrev_table = get_non_null_table(a_inc_stat, 'TotalRevenue')

    _totrev_table_len = _totrev_table.size

    # calculate rev growth rates via annual revenues
    if not _gp_table.empty:
        gp_margin = [_gp_table.iloc[i] / _totrev_table.iloc[i]
                     for i in range(_totrev_table_len)]
        _gp_margin_av = np.average(gp_margin)
    else:
        _no_totexp = False
        try:
            _totexp_table = a_inc_stat['TotalExpenses']
        except KeyError:
            _totexp_table = _totrev_table  # no gp margin and no total expenses
            _no_totexp = True

        gp_margin = [_totrev_table.iloc[i] - _totexp_table.iloc[i] / _totrev_table.iloc[i]
                     for i in range(_totrev_table_len)]
        _gp_margin_av = np.average(gp_margin)
        if _no_totexp:
            _gp_margin_av = float('nan')

    # calculate free cashflow margin for latest years
    if not _fcf_table.empty:
        try:
            fcf_margin = [_fcf_table.iloc[i] / _totrev_table.iloc[i]
                          for i in range(_totrev_table_len)]
            _fcf_margin_av = np.average(fcf_margin)
        except IndexError:
            pass
    else:
        _fcf_margin_av = float('nan')

    return _gp_margin_av, _fcf_margin_av


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
