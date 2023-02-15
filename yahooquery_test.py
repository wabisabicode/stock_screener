#import yahooquery as yq
from yahooquery import Ticker
import numpy as np
import math

norm = 1000000

for stockname in ['abbv', 'alv.de', 'mo', 'amt']:#, 'googl']:
    stock = Ticker(stockname)

#    print(stock.summary_detail)

    # get yearly-relevant data: Inventory and TotalRevenue
#    types_yearly = ['Inventory', 'TotalRevenue']
#
#    yearly_info = stock.get_financial_data(types_yearly, trailing = True).tail(2)
#    rev_last_y, rev_now = yearly_info['TotalRevenue']
##    print(yearly_info)
#
#    while True: 
#        try:
#            inv_last_y, inv_now = yearly_info['Inventory']
#            break
#        except KeyError:
#            inv_last_y = 0
#            inv_now = 0
#            break

    # get asset profile
    ebitda = stock.financial_data[stockname]['ebitda']

    # revenue has to be summed up
    types_tosum = ['TotalRevenue','Inventory']
    tosum_info = stock.get_financial_data(types_tosum, frequency='q', trailing=False)
    
    rev = tosum_info.tail(4)['TotalRevenue']
    tot_rev = np.sum(rev)
    rev_mrq = rev[-1]

    # calculate inventory as % of last quarter revenue and ttm average thereof
    av_inv_to_rev = 0.
    inv_to_rev_mrq = 0.
    while True:
        try:
            inv = tosum_info.tail(4)['Inventory'].copy() # unpack inventory for 4 last quarters
            inv_mrq = inv[-1]
            if math.isnan(inv_mrq): inv_mrq = inv[-1] = inv[-2]
       
            for i in [0, 1, 2, 3]: av_inv_to_rev += inv[i] / rev[i]
            av_inv_to_rev = av_inv_to_rev / 4
            inv_to_rev_mrq = inv_mrq / rev_mrq
            break
        except KeyError:
            break
    
    # get TTM-relevant data

    types = ['CashAndCashEquivalents', 'TotalLiabilitiesNetMinorityInterest', 'TotalEquityGrossMinorityInterest', 'TotalDebt', 'OperatingCashFlow', 'FreeCashFlow']

    quartal_info = stock.get_financial_data(types, frequency='q', trailing=False)

#    print (quartal_info)

    #check if period type has ttm
    
#    inv = []
#    while True:
#        try:
#            inv = quartal_info['Inventory']
#            break
#        except KeyError:
#            inv = 0
#            break    
#
#    print (inv)

    cash = quartal_info['CashAndCashEquivalents'].iloc[-1]
    liability = quartal_info['TotalLiabilitiesNetMinorityInterest'].iloc[-1] 
    equity = quartal_info['TotalEquityGrossMinorityInterest'].iloc[-1]
    totalDebt = quartal_info['TotalDebt'].iloc[-1]
    asOfDate = quartal_info['asOfDate'].iloc[-1]

    print (tot_rev/norm, ebitda/norm, cash/norm, 
            "{:,.2f}%".format(av_inv_to_rev*100), "{:,.2f}%".format(inv_to_rev_mrq*100), 
            liability/norm, equity/norm, totalDebt/norm, asOfDate.strftime('%m/%y'), sep=' \t ')

#    interest = quartal_info['InterestExpense']
#    d_and_a = quartal_info['DepreciationAndAmortization']
#    ocf = quartal_info['OperatingCashFlow']
#    fcf = quartal_info['FreeCashFlow']
