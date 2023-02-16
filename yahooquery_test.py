#import yahooquery as yq
from yahooquery import Ticker
import numpy as np
import math

def main():
    for stockname in ['abbv', 'alv.de', 'mo', 'amt', 'amgn', 'ay', 'bti', 'blk', 'bepc', 'csco', 'dlr', 'enb', 'ecv.de', 'hei.de', 'ibe.mc']:#, 'googl']:

        stock = Ticker(stockname)

        av_inv_to_rev, inv_to_rev_mrq = calc_revenue_inventory_stats(stock)

        ebitda = get_ttm_ebitda(stock, stockname)
       
        equity_ratio, net_debt, asOfDate = get_mrq_financial_strength(stock)

        print ("{} \t {:5.0f}% \t {:4.1f} \t {:6.1f}% \t {:6.1f}%".format(
                stockname, 
                equity_ratio * 100, net_debt / ebitda,
                av_inv_to_rev * 100, inv_to_rev_mrq * 100), 
                asOfDate.strftime('%m/%y'), sep=' \t ')

    #    norm = 1000000
    #    print (stockname, tot_rev/norm, ebitda/norm, cash/norm, 
    #            "{:,.2f}%".format(av_inv_to_rev*100), "{:,.2f}%".format(inv_to_rev_mrq*100), 
    #            liability/norm, equity/norm, totalDebt/norm, asOfDate.strftime('%m/%y'), sep=' \t ')


#***********************************************
#****   get ttm ebitda from asset profile   ****
#***********************************************
def get_ttm_ebitda(_stock, _stockname):

    _ebitda = _stock.financial_data[_stockname]['ebitda']

    return _ebitda


#***********************************************
#****   get ttm ebitda from asset profile   ****
#***********************************************
def get_mrq_financial_strength(_stock):

    # get most recent quarter cash, liabilities, equity, debt 
    types = ['CashAndCashEquivalents', 'TotalLiabilitiesNetMinorityInterest', 'TotalEquityGrossMinorityInterest', 'TotalDebt', 'OperatingCashFlow', 'FreeCashFlow']
    quartal_info = _stock.get_financial_data(types, frequency='q', trailing=False)

#    print (quartal_info)

    cash = quartal_info['CashAndCashEquivalents'].iloc[-1]
    liability = quartal_info['TotalLiabilitiesNetMinorityInterest'].iloc[-1] 
    equity = quartal_info['TotalEquityGrossMinorityInterest'].iloc[-1]
    totalDebt = quartal_info['TotalDebt'].iloc[-1]
#    ocf = quartal_info['OperatingCashFlow']
#    fcf = quartal_info['FreeCashFlow']

    _asOfDate = quartal_info['asOfDate'].iloc[-1]
    _equity_ratio = equity / (equity + liability)
    _net_debt = totalDebt - cash

    return _equity_ratio, _net_debt, _asOfDate


def calc_revenue_inventory_stats(_stock):
    # revenue has to be summed up
    types_tosum = ['TotalRevenue','Inventory']
    tosum_info = _stock.get_financial_data(types_tosum, frequency='q', trailing=False)

#    print (tosum_info)

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
#            print ("Empty array")
            break

    # calculate inventory as % of last quarter revenue and ttm average thereof
    _av_inv_to_rev = 0.
    _inv_to_rev_mrq = 0.

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

    return _av_inv_to_rev, _inv_to_rev_mrq

if __name__ == "__main__":
    main()
