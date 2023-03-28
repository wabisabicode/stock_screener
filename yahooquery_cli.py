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
    print ("stock \t qrGr-yoy \t rGrYav \t qGrMarg \t eq/totAs \t n/ebitda \t aInv/Rev \t inv/RevMRQ")

    # Get stats for the stocks in the list
    for stockname in stocks_list:
        if stockname != '':

            stock = Ticker(stockname)

            fin_data = stock.financial_data[stockname]

            # get info from the financial data
            ebitda = get_ttm_ebitda(fin_data)
            q_rev_growth = get_q_rev_growth(fin_data)
          
            # get margins from income statement
            mrq_gp_margin = get_mrq_gp_margin(stock)

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

            print ("{} \t {:5.0f}% \t {:5.0f}% \t {:5.0f}% \t {:5.0f}% \t {:6.1f} \t {:5.0f}% \t {:5.0f}% ".format(
                    stockname, q_rev_growth * 100, av_rev_growth * 100 - 100,
                    mrq_gp_margin * 100, 
                    equity_ratio * 100, net_debt_to_ebitda,
                    av_inv_to_rev * 100, inv_to_rev_mrq * 100), 
                    asOfDate.strftime('%m/%y'), "\t {}".format(remarks), sep=' \t ')

        #    norm = 1000000
        #    print (stockname, tot_rev/norm, ebitda/norm, cash/norm, 
        #            "{:,.2f}%".format(av_inv_to_rev*100), "{:,.2f}%".format(inv_to_rev_mrq*100), 
        #            liability/norm, equity/norm, totalDebt/norm, asOfDate.strftime('%m/%y'), sep=' \t ')

        else:
            print(' ')


# ----------------------------------------------
# get ttm ebitda from asset profile
# ----------------------------------------------

def get_ttm_ebitda(_fin_data):

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

    return _ebitda

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

# ----------------------------------------------
# get gross profit margin of the mrq (or ttm)
# ----------------------------------------------

def get_mrq_gp_margin(_stock):

    quartal_info = _stock.income_statement(frequency='q', trailing=False)

    # if quartal_info is a string (Income Statement data unavailable for _stock)
    # use trailing info instead of the mrq
    if isinstance(quartal_info,str): 
        quartal_info = _stock.income_statement(frequency='q', trailing=True)

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

    return _mrq_gp_margin

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

    _av_rev_growth = np.prod(r_growth) ** (1./(num_years - 1))

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
            rev = tosum_info.tail(4)['TotalRevenue']
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
            inv = tosum_info.tail(4)['Inventory'].copy() # unpack inventory for 4 last quarters
            inv_mrq = inv[-1]
            if math.isnan(inv_mrq): inv_mrq = inv[-1] = inv[-2]
       
            for i in [0, 1, 2, 3]: _av_inv_to_rev += inv[i] / rev[i]
            _av_inv_to_rev = _av_inv_to_rev / 4
            _inv_to_rev_mrq = inv_mrq / rev_mrq
            break
        except KeyError:
            break

    return _av_inv_to_rev, _inv_to_rev_mrq, _remark

if __name__ == "__main__":
    main()
