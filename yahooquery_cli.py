from yahooquery import Ticker
import numpy as np
import math
import sys
import argparse

def main():

    # Initialize parser
    parser = argparse.ArgumentParser()

    # Passing a shortname of a stockslist (or stock symbols)
    listarg = []
    parser.add_argument("-l", nargs="*", help = "Stocks list name: div, growth, rest, watch, watchgrow, watchcomm or stock symbol")
    args = parser.parse_args()
    listarg = args.l
   
    # Fill in a list of stocks based on the input option 
    stocks_list = []

    if listarg[0] == "div":
        stocks_list = ['abbv', 'alv.de', 'mo', 'amt', 'amgn', 'ay', 'bti', 'blk', 'bepc', 'csco', 'dlr', 'enb', 'ecv.de', 
        'hei.de', 'ibe.mc', 'intc', 'irm', 'kmi', '8001.t', 'lvmhf', 'mpw', '4091.t', 'ohi', 'spg', 'swa.de', 'swk', 'ul']
    elif listarg[0] == "growth":
        stocks_list = ['adbe', 'abnb', 'googl', 'amzn', 'asml', 'bntx', 'sq', 'coin', 'c0m.de', 'hyq.de', 'ma', 'meta', 'pltr', 'veev']
    elif listarg[0] == "rest":
        stocks_list = ['eqnr', '', 'rio', '', '', 'arcc', 'ocsl']
    elif listarg[0] == "watch":
        stocks_list = ['tte', 'shel', '', '', 'apd', 'lin', 'bas.de', '', '', 'mmm', 'dpw.de', 'fra.de', 'ge', 'hot.de', 'lmt', 'raa.de', 
                '', '', 'mcd', 'ads.de', 'prx.as', 'sbux', 'vfc', '', '', '2502.t', 'ko', 'k', 'nesn.sw', 'pep', 'pm', '', '',
                'bayn.de', 'bion.sw', 'bmy', 'gild', 'jnj', 'nvs', 'rog.sw', 'soon.sw', '', '', 'brk-b', 'ms', 'muv2.de', '', '',
                'dell', '4901.t', 'ibm', 'msft', 'txn', '', '', 't', 'dte.de', 'dis', 'vz', '', '', 'bipc', 'ibe.mc', 'red.mc', '', '',
                'amt', 'avb', 'dea', 'krc', 'nnn', 'stag', 'skt', 'vici', 'vna.de', 'wpc']
    elif listarg[0] == "watchgrow":
        stocks_list = ['bkng', 'bidu', 'cdr.wa', 'crwd', 'hcp', 'splk', 'baba', 'tdoc', 'tcehy', 'tsla', 'twlo', 'pton', 'upst', 'vmeo',
                'isrg', '6060.hk', 'aapl', 'nem.de', 'nvda', 'var1.de', 'estc', 'hfg.de', 'qlys', 'pypl', 'zal.de', 'zm']
    elif listarg[0] == "watchcomm":
        stocks_list = ['eog']
    else:
        stocks_list = listarg

    # print header
    print ("stock\tqRGrYoY\t aRGrY \t mrqGM \t avGMy \t mrqOCF\t avOCFy\t mrqFCF\t avFCFy\t eq/toA\tnebitda\t aIn/R\tin/Rmrq\tEV/Sale\t P/OCF\t  mrq\tRemark")

    # Get stats for the stocks in the list
    for stockname in stocks_list:
        if stockname != '':

            stock = Ticker(stockname, asynchronous=True)

            fin_data = stock.financial_data[stockname]

            # get info from the financial data
            ebitda, ocf = get_ttm_ebitda_ocf(fin_data)
            q_rev_growth = get_q_rev_growth(fin_data)
         
            # get current valuations for EV-to-Rev and Price/OCF
            key_stats = stock.key_stats[stockname]
            ev_to_rev = get_ev_to_rev(key_stats)            

            summary_detail = stock.summary_detail[stockname]
            p_to_ocf = get_p_to_ocf(summary_detail, ocf)

            # get margins from income statement
            mrq_gp_margin, mrq_ocf_margin, mrq_fcf_margin = get_mrq_gp_margin(stock)
            av_gp_margin, av_ocf_margin, av_fcf_margin = get_yearly_gp_margin(stock)

            # get info from income, balance and cashflow 
            av_rev_growth, remark_rev = get_yearly_revenue(stock)
            av_inv_to_rev, inv_to_rev_mrq, remark_inv = calc_revenue_inventory_stats(stock)
            equity_ratio, net_debt, asOfDate = get_mrq_financial_strength(stock)

            # get valuations
#            getValuations(asOfDate)

            # check if ebitda is zero
            if ebitda:
                net_debt_to_ebitda = net_debt / ebitda
            else:
                net_debt_to_ebitda = float('inf')

            # join remarks
            remarks = remark_rev + ' ' + remark_inv

            print ("{}\t {:3.0f}% \t {:3.0f}% \t {:4.0f}% \t {:4.0f}% \t {:4.0f}% \t {:4.0f}% \t {:4.0f}% \t {:4.0f}% \t {:4.0f}% \t {:5.1f} \t {:3.0f}% \t {:3.0f}% \t {:5.2f} \t {:5.2f} ".format(
                    stockname, q_rev_growth * 100, av_rev_growth * 100 - 100,
                    mrq_gp_margin * 100, av_gp_margin * 100,
                    mrq_ocf_margin * 100, av_ocf_margin * 100,
                    mrq_fcf_margin * 100, av_fcf_margin * 100,
                    equity_ratio * 100, net_debt_to_ebitda,
                    av_inv_to_rev * 100, inv_to_rev_mrq * 100, 
                    ev_to_rev, p_to_ocf), 
                    asOfDate.strftime('%m/%y'), "\t{}".format(remarks))

        #    norm = 1000000
        #    print (stockname, tot_rev/norm, ebitda/norm, cash/norm, 
        #            "{:,.2f}%".format(av_inv_to_rev*100), "{:,.2f}%".format(inv_to_rev_mrq*100), 
        #            liability/norm, equity/norm, totalDebt/norm, asOfDate.strftime('%m/%y'), sep=' \t ')

        else:
            print(' ')


# ----------------------------------------------
# get ttm ebitda and ocf from asset profile
# ----------------------------------------------

def get_ttm_ebitda_ocf(_fin_data):

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
            _ocf = 0.
            break
        except ValueError:
            _ocf = 0.
            break

    return _ebitda, _ocf

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

    return _q_rev_growth

def get_ev_to_rev(_key_stats):

    while True:
        try:
            _ev_to_rev = _key_stats['enterpriseToRevenue']
            break
        except KeyError:
            _ev_to_rev = 0.
            break
        except ValueError:
            _ev_to_rev = 0.
            break

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


    return _p_to_ocf

# ----------------------------------------------
# get gross profit margin of the mrq (or ttm)
# ----------------------------------------------

def get_mrq_gp_margin(_stock):

    quartal_info = _stock.income_statement(frequency='q', trailing=False)
    quartal_cf = _stock.cash_flow(frequency='q', trailing=False)

    # if quartal_info is a string (Income Statement data unavailable for _stock)
    # use trailing info instead of the mrq
    if isinstance(quartal_info,str): 
        quartal_info = _stock.income_statement(frequency='q', trailing=True)
        quartal_cf = _stock.cash_flow(frequency='q', trailing=True)

    # get Gross Profit
    while True:
        try:
            _mrq_gp  = quartal_info['GrossProfit'].iloc[-1] 
            break
        except KeyError:
            _mrq_gp = 0.
            break
        except ValueError:
            _mrq_gp = 0.
            break

    # get Operating CashFlow
    while True:
        try:
            _mrq_ocf  = quartal_cf['OperatingCashFlow'].iloc[-1] 
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
            _mrq_fcf  = quartal_cf['FreeCashFlow'].iloc[-1] 
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
            _mrq_rev = quartal_info['TotalRevenue'].iloc[-1]
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

#    print(yearly_info)
    # get Gross Profit table
    no_gp = False
    while True:
        try:
            _gp_table = yearly_info['GrossProfit']
            break
        except KeyError:
            no_gp = True
#            print("KeyError")
            break
        except ValueError:
            no_gp = True
#            print("ValueError")
            break

    # get Operating Cashflow
    yearly_cf = _stock.cash_flow(frequency='a', trailing=False)

    no_ocf = False
    while True:
        try:
            _ocf_table = yearly_cf['OperatingCashFlow']
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
            _fcf_table = yearly_cf['FreeCashFlow']
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
            _totrev_table = yearly_info['TotalRevenue']
            break
        except KeyError:
            _totrev_table = 0
            break
        except ValueError:
            _totrev_table = 0
            break

    # calculate rev growth rates via annual revenues
    if (no_gp == False):
        gp_margin = []

        for i in range(len(_totrev_table)-1, -1, -1):
            gp_margin.append(_gp_table[i]/_totrev_table[i])

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
        for i in range(len(_totrev_table)-1, -1, -1):
            gp_margin.append((_totrev_table[i]-_totexp_table[i])/_totrev_table[i])
        _gp_margin_av = np.average(gp_margin)
        if _no_totexp: _gp_margin_av = float('nan')

    # calculate operating cashflow margin for latest years
    if (no_ocf == False):
        ocf_margin = []

        for i in range(len(_totrev_table)-1, -1, -1):
            ocf_margin.append(_ocf_table[i]/_totrev_table[i])
    
        _ocf_margin_av = np.average(ocf_margin)
    else:
        _ocf_margin_av = float('nan')

    # calculate free cashflow margin for latest years
    if (no_fcf == False):
        fcf_margin = []

        for i in range(len(_totrev_table)-1, -1, -1):
            fcf_margin.append(_fcf_table[i]/_totrev_table[i])
    
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

    # calculate rev growth rates via annual revenues
    r_growth = []

    for i in range(len(revs) - 1, 0, -1):
        r_growth.append(revs[i]/revs[i-1])

    _r_growth_tot = np.prod(r_growth)

    if (_r_growth_tot > 0.):
        _av_rev_growth = np.prod(r_growth) ** (1./(num_years - 1))
    else:
        _av_rev_growth = float('nan')

    _remark_rev = str(num_years) + 'Yrev'

    return _av_rev_growth, _remark_rev

def calc_revenue_inventory_stats(_stock):
    # revenue has to be summed up
    types_tosum = ['TotalRevenue','Inventory']
    tosum_info = _stock.get_financial_data(types_tosum, frequency='q', trailing=False)

    # check how many quarterly data is there
    if type(tosum_info) is not str:
        num_quarters = tosum_info.shape[0]
    else:
        num_quarters = 0

    _remark = 'inv'+ str(num_quarters) + 'Q'

    # calculate ttm revenue and mrq revenue
    tot_rev = 0
    rev_mrq = 0
    no_rev_data = False

    while True:
        try: 
#            rev = tosum_info.tail(4)['TotalRevenue']
            rev = tosum_info['TotalRevenue']
            tot_rev = np.sum(rev)
            rev_mrq = rev[-1]
            break
        except KeyError:
            no_rev_data = True
            break
        except AttributeError:
            no_rev_data = True
            break

    # calculate inventory as % of mrq revenue and ttm average thereof
    _av_inv_to_rev = 0.
    _inv_to_rev_mrq = 0.

    if no_rev_data == True:
        _av_inv_to_rev = _inv_to_rev_mrq = float('nan')

    while True and no_rev_data == False:
        try:
#            inv = tosum_info.tail(4)['Inventory'].copy() # unpack inventory for 4 last quarters
            inv = tosum_info['Inventory'].copy() # unpack inventory for 4 last quarters
            inv_mrq = inv[-1]
            if math.isnan(inv_mrq): inv_mrq = inv[-1] = inv[-2]

            _inv_to_rev = []
            for i in range(len(inv)-1, -1, -1):
                _inv_to_rev.append(inv[i] / rev[i])
            _av_inv_to_rev = np.average(_inv_to_rev)

            _inv_to_rev_mrq = inv_mrq / rev_mrq
            break
        except KeyError:
            break

    return _av_inv_to_rev, _inv_to_rev_mrq, _remark

if __name__ == "__main__":
    main()
