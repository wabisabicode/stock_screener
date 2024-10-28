import argparse
import math

import numpy as np
from yahooquery import Ticker


def main():
    display_table_header()

    # Initialize parser
    parser = argparse.ArgumentParser()

    # Passing a shortname of a stockslist (or stock symbols)
    listarg = []
    parser.add_argument("-l", nargs="*",
                        help=("Stocks list name: div, growth, rest, watch,"
                              "watchgrow, watchcomm or stock symbol"))
    args = parser.parse_args()
    listarg = args.l

    stocks_list = form_stock_list(listarg[0])

    # Get stats for the stocks in the list
    for stockname in stocks_list:
        if stockname != '':
            stock = Ticker(stockname, asynchronous=False)

            fin_data = stock.financial_data[stockname]

            # get info from the financial data
            ebitda, ocf, tot_rev = get_ttm_ebitda_ocf(stock, fin_data)
            q_rev_growth = get_q_rev_growth(fin_data)

            # get current valuations for EV-to-Rev and Price/OCF
            if (stockname != 'bion.sw'):
                key_stats = stock.key_stats[stockname]
            else:
                key_stats = 0

            ev_to_rev = get_ev_to_rev(stock, key_stats)

            summary_detail = stock.summary_detail[stockname]
            p_to_ocf = get_p_to_ocf(summary_detail, ocf)

            # get margins from income statement
            mrq_gp_margin, mrq_ocf_margin, mrq_fcf_margin = get_mrq_gp_margin(stock)
            av_gp_margin, av_ocf_margin, av_fcf_margin = get_yearly_gp_margin(stock)

            # get info from income, balance and cashflow 
            av_rev_growth, remark_rev = get_yearly_revenue(stock)
            av_inv_to_rev, inv_to_rev_mrq, remark_inv = calc_revenue_inventory_stats(stock)
            equity_ratio, net_debt, asOfDate = get_mrq_financial_strength(stock)

            # check if ebitda is zero
            if ebitda:
                net_debt_to_ebitda = net_debt / ebitda
            else:
                net_debt_to_ebitda = float('inf')

            # join remarks
            remarks = remark_rev + ' ' + remark_inv

            print(
                "{}\t ".format(stockname),
                "{:4.0f}%\t{:5.1f} \t {:3.0f}% \t {:3.0f}% \t\t".format(
                    equity_ratio * 100, net_debt_to_ebitda, inv_to_rev_mrq * 100, av_inv_to_rev * 100),
                "{:3.0f}% \t {:3.0f}% \t".format(
                    q_rev_growth * 100, av_rev_growth * 100 - 100),
                "{:4.0f}% \t {:4.0f}% \t {:4.0f}% \t {:4.0f}% \t {:4.0f}% \t {:4.0f}% \t".format(
                    mrq_gp_margin * 100, av_gp_margin * 100,
                    mrq_ocf_margin * 100, av_ocf_margin * 100, mrq_fcf_margin * 100, av_fcf_margin * 100),
                asOfDate.strftime('%m/%y'), "\t{}\t\t".format(remarks),
                "{:5.2f}\t{:6.2f}".format(ev_to_rev, p_to_ocf)
                )
        else:
            print(' ')


def form_stock_list(_listarg):
    # Fill in a list of stocks based on the input option 
    _stocks_list = []

    if _listarg == "div":
        _stocks_list = ['abbv', 'are', 'alv.de', 'mo', 'amt', 'amgn', 'bti',
                        'blk', 'bepc', 'csco', 'cvs', 'enb', 'ibe.mc', 'intc',
                        'kmi', '8001.t', 'lvmhf', 'mpw', '4091.t', 'nnn',
                        'ohi', 'pfe', 'spg', 'swk', 'ul', 'vna.de']
    elif _listarg == "growth":
        _stocks_list = ['adbe', 'abnb', 'googl', 'amzn', 'asml', 'bntx', 'sq',
                        'net', 'coin', 'dis', 'hyq.de', 'ma', 'veev', 'vmeo']
    elif _listarg == "rest":
        _stocks_list = ['eqnr', '', 'rio', '', '', 'arcc', 'ocsl']
    elif _listarg == "watch":
        _stocks_list = ['tte', 'shel', '', '', 'apd', 'hei.de', 'lin',
                        'bas.de', '', '', 'mmm', 'dhl.de', 'fra.de', 'ge',
                        'hot.de', 'lmt', 'raa.de', '', '', 'mcd', 'ads.de',
                        'prx.as', 'sbux', 'vfc', '', '', '2502.t', 'ko', 'k',
                        'nesn.sw', 'pep', 'pm', 'swa.de', '', '', 'bayn.de',
                        'bion.sw', 'bmy', 'gild', 'jnj', 'nvs', 'rog.sw',
                        'soon.sw', '', '', 'brk-b', 'ms', 'muv2.de', '', '',
                        'dell', '4901.t', 'hpq', 'ibm', 'meta', 'msft', 'txn',
                        '', '', 't', 'dte.de', 'iac', 'g24.de', 'vz', 'wbd',
                        '', '', 'bipc', 'nee', 'red.mc', 'ay', '', '', 'avb',
                        'dlr', 'irm', 'dea', 'hr', 'krc', 'stag', 'skt',
                        'vici', 'wpc']
    elif _listarg == "watchgrow":
        _stocks_list = ['baba', 'aapl', 'bkng', 'bidu', 'cdr.wa', 'crwd',
                        'estc', 'hcp', 'hfg.de', 'isrg', 'nem.de', 'nvda',
                        'pltr', 'pypl', 'pton', 'qlys', 'splk', 'tmv.de',
                        'tdoc', 'tcehy', 'tsla', 'twlo', 'uber', 'upst',
                        'var1.de', 'zal.de', '6060.hk', 'zm']
    elif _listarg == "watchcomm":
        _stocks_list = ['eog']
    else:
        _stocks_list = [_listarg]

    return _stocks_list


def display_table_header():
    print("     \t  | debt health |   inv-to-Rev\t |\tRev Growth     |"
          " Gross Margin  |  Op CashFlow  | Free CashFlow |"
          "\t    \t     \t  |       Valuation\t")
    print("stock\t    eqR\tnebitda\t i/Rmrq\t aIn/R\t\tqRGrYoY\t aRGrY "
          "\t mrqGM \t avGMy \t mrqOCF\t avOCFy\t mrqFCF\t avFCFy\t mrq"
          "\t Remark \t\tEV/Sale\t P/OCF")


# ----------------------------------------------
# get ttm ebitda and ocf from asset profile
# ----------------------------------------------
def get_ttm_ebitda_ocf(_stock, _fin_data):

    while True:
        try:
            _ebitda = _fin_data['ebitda']
            break
        except KeyError:
            _ebitda = 0.
            break
        except ValueError:
            _ebitda = 0.
            break

    while True:
        try:
            _ocf = _fin_data['operatingCashflow']
            break
        except KeyError:
            quartal_cf = _stock.cash_flow(frequency='q', trailing=True)
            quartal_cf = quartal_cf[quartal_cf['periodType'] == 'TTM']  # leave TTM-only values
            try:
                _ocf  = quartal_cf['OperatingCashFlow'].iloc[-1]
            except:
                _ocf = 0.
            if np.isnan(_ocf):
                try:
                    _ocf  = quartal_cf['OperatingCashFlow'].iloc[-2]
                except:
                    _ocf = 0.
            break
        except ValueError:
            _ocf = 0.
            break

    while True:
        try:
            _tot_rev = _fin_data['totalRevenue']
            break
        except KeyError:
            _tot_rev = 0.
            break
        except ValueError:
            _tot_rev = 0.
            break

    return _ebitda, _ocf, _tot_rev


def get_ttm_rev(_stock):

    income_stat = _stock.income_statement(frequency='q', trailing=True)

    while True:
        try:
            _tot_rev = income_stat['TotalRevenue'].iloc[-1]
            break
        except KeyError:
            _tot_rev = 0.
            break
        except ValueError:
            _tot_rev = 0.
            break

    return _tot_rev


def get_q_rev_growth(_fin_data):
    """ get yoy revenue growth for the most recent quarter 
    """

    while True:
        try:
            _q_rev_growth = _fin_data['revenueGrowth']
            break
        except KeyError:
            _q_rev_growth = 0.
            break
        except ValueError:
            _q_rev_growth = 0.
            break

    # check if _q_rev_growth is an (empty) dict
    if type(_q_rev_growth) is dict:
            _q_rev_growth = 0.

    return _q_rev_growth


def get_ev_to_rev(_stock, _key_stats):
    """ get EV to Rev. If it is absent in key_stats,
    we get it from table valuation_measures
    an alternative way would be to get EV and TotRev separately.
    This way is commented out. Maybe useful for later development
    """ 

    no_evrev = False
    try:
        _ev_to_rev = _key_stats['enterpriseToRevenue']
    except KeyError:
        _ev_to_rev = 0.
        no_evrev = True
    except ValueError:
        _ev_to_rev = 0.
        no_evrev = True
    except TypeError:
        _ev_to_rev = 0.
        no_evrev = True

#    print(_stock.valuation_measures)

    # check if no ev-to-rev exist or if it is an empty dict
    if no_evrev or not bool(_ev_to_rev):
        try:
            _ev_to_rev = _stock.valuation_measures['EnterprisesValueRevenueRatio'].iloc[-1]
        except:
            _ev_to_rev = float('nan')
            
#    _ev = _stock.valuation_measures['EnterpriseValue'].iloc[-2]
#    _ev_to_rev2 = 0.
#    if no_rev:
#        try:
#            _ev_to_rev2 = _ev / _tot_rev_backup
#        except ZeroDivisionError:
#            _ev_to_rev2 = float('nan')
#    print (_ev_to_rev, _ev_to_rev2)

#    print (' ')
#    print (_ev_to_rev)

    return _ev_to_rev


def get_p_to_ocf(_summary_detail, _ocf):

    while True:
        try:
            _m_cap = _summary_detail['marketCap']
            break
        except KeyError:
            _m_cap = 0.
            break
        except ValueError:
            _m_cap = 0.
            break

    try: 
        _p_to_ocf = _m_cap / _ocf
    except ZeroDivisionError:
        _p_to_ocf = float('nan')
    except TypeError:
        _p_to_ocf = float('nan')

    return _p_to_ocf


# ----------------------------------------------
# get gross profit margin of the mrq (or ttm)
# ----------------------------------------------
def get_mrq_gp_margin(_stock):

    quartal_info = _stock.income_statement(frequency='q', trailing=False)
    quartal_cf = _stock.cash_flow(frequency='q', trailing=False)

    # if quartal_info is str (Income Statement data unavailable for _stock)
    # use trailing info instead of the mrq
    if isinstance(quartal_info, str):
        quartal_info = _stock.income_statement(frequency='q', trailing=True)
        quartal_cf = _stock.cash_flow(frequency='q', trailing=True)

    # get Gross Profit
    while True:
        try:
            _mrq_gp = quartal_info['GrossProfit'].dropna().iloc[-1]
            break
        except KeyError:
            _mrq_gp = 0.
            break
        except ValueError:
            _mrq_gp = 0.
            break

#    print (quartal_cf)
    # get Operating CashFlow
    while True:
        try:
            ocf_cleaned = quartal_cf['OperatingCashFlow'].dropna()
            _mrq_ocf = ocf_cleaned.iloc[-1]
            break
        except KeyError:
            _mrq_ocf = 0.
            break
        except ValueError:
            _mrq_ocf = 0.
            break

    # get Operating CashFlow
    while True:
        try:
            _mrq_fcf = quartal_cf['FreeCashFlow'].dropna().iloc[-1] 
            break
        except KeyError:
            _mrq_fcf = 0.
            break
        except ValueError:
            _mrq_fcf = 0.
            break

    # get Total Revenue
    while True:
        try:
            _mrq_rev = quartal_info['TotalRevenue'].dropna().iloc[-1]
            # global quartal_rev
            # quartal_rev = _mrq_rev
            # print(_mrq_rev)
            break
        except KeyError:
            _mrq_rev = 0.
            break
        except ValueError:
            _mrq_rev = 0.
            break
    
    # calculate mrq gross profit margin
    if (_mrq_gp > 0.):
        _mrq_gp_margin = _mrq_gp / _mrq_rev
    else:
        _mrq_gp_margin = float('nan')

    # calculate mrq operating cf margin
#    if (_mrq_ocf > 0.):
    _mrq_ocf_margin = _mrq_ocf / _mrq_rev
#    else:
#        _mrq_ocf_margin = float('nan')

    # calculate mrq operating cf margin
#    if (_mrq_fcf > 0.):
    _mrq_fcf_margin = _mrq_fcf / _mrq_rev
#    else:
#        _mrq_fcf_margin = float('nan')

    return _mrq_gp_margin, _mrq_ocf_margin, _mrq_fcf_margin


# ----------------------------------------------
# get gross profit margin of the mrq (or ttm)
# ----------------------------------------------
def get_yearly_gp_margin(_stock):

    yearly_info = _stock.income_statement(frequency='a', trailing=False)

    # get Gross Profit table
    no_gp = False
    while True:
        try:
            _gp_table = yearly_info['GrossProfit'].dropna()
            break
        except KeyError:
            no_gp = True
            break
        except ValueError:
            no_gp = True
            break

    # get Operating Cashflow
    yearly_cf = _stock.cash_flow(frequency='a', trailing=False)

    no_ocf = False
    while True:
        try:
            _ocf_table = yearly_cf['OperatingCashFlow'].dropna()
            break
        except KeyError:
            no_ocf = True
            break
        except ValueError:
            no_ocf = True
            break

    # get Free Cashflow
    no_fcf = False
    while True:
        try:
            _fcf_table = yearly_cf['FreeCashFlow'].dropna()
            break
        except KeyError:
            no_fcf = True
            break
        except ValueError:
            no_fcf = True
            break


    # get Total Revenue table
    while True:
        try:
            _totrev_table = yearly_info['TotalRevenue'].dropna()
            break
        except KeyError:
            _totrev_table = 0
            break
        except ValueError:
            _totrev_table = 0
            break

    _totrev_table_len = _totrev_table.size

    # calculate rev growth rates via annual revenues
    if (no_gp == False):
        gp_margin = []

        for i in range(_totrev_table_len - 1, -1, -1):
            gp_margin.append(_gp_table.iloc[i]/_totrev_table.iloc[i])

        _gp_margin_av = np.average(gp_margin)
    else:
        _no_totexp = False
        while True:
            try:
                _totexp_table = yearly_info['TotalExpenses']
                break
            except KeyError:
                _totexp_table = _totrev_table   # if no gp margin and no total expenses, make gp margin be 0
                _no_totexp = True
                break

        gp_margin = []
        for i in range(_totrev_table_len - 1, -1, -1):
            gp_margin.append((_totrev_table.iloc[i]-_totexp_table.iloc[i])/_totrev_table.iloc[i])
        _gp_margin_av = np.average(gp_margin)
        if _no_totexp: _gp_margin_av = float('nan')

    # calculate operating cashflow margin for latest years
    if (no_ocf == False):
        ocf_margin = []

        for i in range(_totrev_table_len - 1, -1, -1):
            try: 
                ocf_margin.append(_ocf_table.iloc[i]/_totrev_table.iloc[i])
            except IndexError:
                pass
    
        _ocf_margin_av = np.average(ocf_margin)
    else:
        _ocf_margin_av = float('nan')

    # calculate free cashflow margin for latest years
    if (no_fcf == False):
        fcf_margin = []

        for i in range(_totrev_table_len - 1, -1, -1):
            try:
                fcf_margin.append(_fcf_table.iloc[i]/_totrev_table.iloc[i])
            except IndexError:
                pass
    
        _fcf_margin_av = np.average(fcf_margin)
    else:
        _fcf_margin_av = float('nan')

    return _gp_margin_av, _ocf_margin_av, _fcf_margin_av


# ----------------------------------------------
# get ttm ebitda from asset profile
# ----------------------------------------------
def get_mrq_financial_strength(_stock):

    # get most recent quarter cash, liabilities, equity, debt 
    types = ['CashAndCashEquivalents', 'TotalLiabilitiesNetMinorityInterest', 
            'TotalEquityGrossMinorityInterest', 'TotalDebt', 'OperatingCashFlow', 'FreeCashFlow']

    quartal_info = _stock.get_financial_data(types, frequency='q', trailing=False)
    
    cash = quartal_info['CashAndCashEquivalents'].iloc[-1]
    liability = quartal_info['TotalLiabilitiesNetMinorityInterest'].iloc[-1] 
    equity = quartal_info['TotalEquityGrossMinorityInterest'].iloc[-1]

    totalDebt = calc_total_debt(quartal_info)

#    ocf = quartal_info['OperatingCashFlow']
#    fcf = quartal_info['FreeCashFlow']

    _asOfDate = quartal_info['asOfDate'].iloc[-1]
    _equity_ratio = equity / (equity + liability)
    _net_debt = totalDebt - cash

    return _equity_ratio, _net_debt, _asOfDate


def calc_total_debt(_quartal_info):

    while True:
        try:
            _totalDebt = _quartal_info['TotalDebt'].iloc[-1]
            break
        except KeyError:
            _totalDebt = float('nan')
            break

    return _totalDebt


def get_yearly_revenue(_stock):
    """ get annual revenues, calculate growth rates 
    and pass average rev growth of passed years"""

    # get annual revenues
    types = ['TotalRevenue']
    yearly_info = _stock.get_financial_data(types, frequency='a', trailing=False)

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


def calc_revenue_inventory_stats(_stock):
    # revenue has to be summed up
    types_tosum = ['TotalRevenue', 'Inventory']
    tosum_info = _stock.get_financial_data(types_tosum, frequency='q', trailing=False)

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
            inv = tosum_info['Inventory'].copy() # unpack inventory for 4 last quarters
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


if __name__ == "__main__":
    main()
