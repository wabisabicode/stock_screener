import math
from datetime import datetime
from .constants import TIME_PROFILE

import numpy as np


# Function to safely extract the last non-null value from a series
def get_last_value(data, key, default=0):
    try:
        return data[key].dropna().iloc[-1]
    except (KeyError, ValueError, IndexError):
        return default


# Function to safely extract a non-null table
def get_non_null_table(data, key, default=0):
    try:
        return data[key].dropna()
    except (KeyError, ValueError):
        return default


# Time profiling
def elapsed_time(time_start, message):
    time_now = datetime.now()
    print(f'{message}:\t{time_now - time_start}')
    return time_now


def timer(func):
    def timer_wrapper(*args, **kwargs):
        if TIME_PROFILE:
            time_start = datetime.now()
            result = func(*args, **kwargs)
            time_end = elapsed_time(time_start, f'{func.__name__} took')
            if func.__name__ == 'update_stock_data':
                print('')
            return result
        else:
            return func(*args, **kwargs)
    return timer_wrapper


# ----------------------------------------------
# get ttm ebitda and ocf from asset profile
# ----------------------------------------------
@timer
def get_ttm_ebitda(_stock, _fin_data):
    # Get EBITDA with default value of 0 if not available
    try:
        _ebitda = _fin_data.get('ebitda', 0.)
    except AttributeError:
        _ebitda = 0.

    return _ebitda


# def get_ttm_rev(_stock):
#     try:
#         income_stat = _stock.income_statement(frequency='q', trailing=True)
#         _tot_rev = income_stat['TotalRevenue'].iloc[-1]
#     except (KeyError, ValueError, IndexError):
#         _tot_rev = 0.

#     return _tot_rev


@timer
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


@timer
def get_ev_to_rev(_key_stats, valuation_measures):
    """Get EV to Revenue ratio. If absent in key_stats, retrieve it from
    the valuation_measures table as an alternative approach.
    """

    try:
        _ev_to_rev = _key_stats['enterpriseToRevenue']
        if isinstance(_ev_to_rev, dict) or not _ev_to_rev:
            _ev_to_rev = None  # Mark for alt. retrieval if empty or dict
    except (KeyError, ValueError, TypeError):
        _ev_to_rev = None  # Mark for alternative retrieval if error occurs

    # If primary retrieval failed, attempt alternative retrieval
    if _ev_to_rev is None:
        _ev_to_rev = get_last_value(valuation_measures, 'EnterprisesValueRevenueRatio', float('nan'))

    return _ev_to_rev


# @timer
# def get_p_to_ocf(valuation_measures, _ocf):
#     _m_cap = get_last_value(valuation_measures, 'MarketCap')

#     try:
#         _p_to_ocf = _m_cap / _ocf
#     except (ZeroDivisionError, TypeError):
#         _p_to_ocf = float('nan')

#     return _p_to_ocf


# ----------------------------------------------
# get gross profit margin of the mrq (or ttm)
# ----------------------------------------------
@timer
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
@timer
def get_ann_gp_margin(_stock, yearly_info, yearly_cf):
    """
    Get annual gross profit margin, operating cash flow margin,
    and free cash flow margin.
    """
    # Extract financial tables
    _gp_table = get_non_null_table(yearly_info, 'GrossProfit', None)
    _ocf_table = get_non_null_table(yearly_cf, 'OperatingCashFlow', None)
    _fcf_table = get_non_null_table(yearly_cf, 'FreeCashFlow', None)
    _totrev_table = get_non_null_table(yearly_info, 'TotalRevenue')

    _totrev_table_len = _totrev_table.size

    # calculate rev growth rates via annual revenues
    if _gp_table is not None:
        gp_margin = [_gp_table.iloc[i] / _totrev_table.iloc[i]
                     for i in range(_totrev_table_len)]
        _gp_margin_av = np.average(gp_margin)
    else:
        _no_totexp = False
        try:
            _totexp_table = yearly_info['TotalExpenses']
        except KeyError:
            _totexp_table = _totrev_table  # no gp margin and no total expenses
            _no_totexp = True

        gp_margin = [_totrev_table.iloc[i] - _totexp_table.iloc[i] / _totrev_table.iloc[i]
                     for i in range(_totrev_table_len)]
        _gp_margin_av = np.average(gp_margin)
        if _no_totexp:
            _gp_margin_av = float('nan')

    # calculate free cashflow margin for latest years
    if _fcf_table is not None:
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
@timer
def get_mrq_fin_strength(_stock, quartal_info):

    cash = get_last_value(quartal_info, 'CashAndCashEquivalents')
    liab = get_last_value(quartal_info, 'TotalLiabilitiesNetMinorityInterest')
    equity = get_last_value(quartal_info, 'TotalEquityGrossMinorityInterest')
    totalDebt = get_last_value(quartal_info, 'TotalDebt', float('nan'))

#    ocf = quartal_info['OperatingCashFlow']
#    fcf = quartal_info['FreeCashFlow']

    _asOfDate = get_last_value(quartal_info, 'asOfDate')
    _equity_ratio = equity / (equity + liab)
    _net_debt = totalDebt - cash

    return _equity_ratio, _net_debt, _asOfDate


@timer
def get_yearly_revenue(_stock, yearly_info):
    """ get annual revenues, calculate growth rates
    and pass average rev growth of passed years"""
    if type(yearly_info) is not str:
        num_years = yearly_info.shape[0]
    else:
        num_years = 0

    revs = yearly_info['TotalRevenue'].iloc[:]
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


@timer
def calc_rev_inv_stats(_stock, tosum_info):

    # check how many quarterly data is there
    if type(tosum_info) is not str:
        num_quarters = tosum_info.shape[0]
    else:
        num_quarters = 0

    _remark = 'inv' + str(num_quarters) + 'Q'

    # calculate ttm revenue and mrq revenue
    rev_mrq = 0
    no_rev_data = False

    if isinstance(tosum_info, str):
        no_rev_data = True
    else:
        try:
            rev = tosum_info['TotalRevenue']
            rev_mrq = rev.iloc[-1]
        except KeyError:
            no_rev_data = True
        except AttributeError:
            no_rev_data = True

    # calculate inventory as % of mrq revenue and ttm average thereof
    _av_inv_to_rev = 0.
    _inv_to_rev_mrq = 0.

    if no_rev_data is False:
        try:
            inv = tosum_info['Inventory'].copy()  # unpack inv for 4 mrq's
            inv_mrq = inv.iloc[-1]
            if math.isnan(inv_mrq):
                inv_mrq = inv.iloc[-1] = inv.iloc[-2]

            _inv_to_rev = []
            for i in range(len(inv)-1, -1, -1):
                _inv_to_rev.append(inv.iloc[i] / rev.iloc[i])
            _av_inv_to_rev = np.average(_inv_to_rev)

            _inv_to_rev_mrq = inv_mrq / rev_mrq
        except KeyError:
            ...
    else:
        _av_inv_to_rev = _inv_to_rev_mrq = float('nan')

    return _av_inv_to_rev, _inv_to_rev_mrq, _remark
