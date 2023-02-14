#import yahooquery as yq
from yahooquery import Ticker

norm = 1000000

stock = Ticker('mo')

print(stock.summary_detail)

# get yearly-relevant data: Inventory and TotalRevenue
types_yearly = ['Inventory', 'TotalRevenue']

yearly_info = stock.get_financial_data(types_yearly, trailing = False).tail(2)

rev_last_y, rev_now = yearly_info['TotalRevenue']
inv_last_y, inv_now = yearly_info['Inventory']

# get TTM-relevant data

types = ['EBITDA', 'CashAndCashEquivalents', 'TotalLiabilitiesNetMinorityInterest', 'CommonStockEquity', 'TotalDebt']

quartal_info = stock.get_financial_data(types, frequency='q', trailing=True)
print (quartal_info)
print ('')

ebitda = quartal_info.tail(1)['EBITDA'][0]
cash = quartal_info['CashAndCashEquivalents'].iloc[-2]
liability = quartal_info['TotalLiabilitiesNetMinorityInterest'].iloc[-2] 
equity = quartal_info['CommonStockEquity'].iloc[-2]
totalDebt = quartal_info['TotalDebt'].iloc[-2]
asOfDate = quartal_info['asOfDate'].iloc[-2]

print (rev_last_y/norm, rev_now/norm, ebitda/norm, cash/norm, inv_last_y/norm, inv_now/norm, liability/norm, equity/norm, totalDebt/norm, asOfDate.strftime('%m/%y'), sep=' \t ')
print (rev_last_y/norm, rev_now/norm, ebitda/norm, cash/norm, inv_last_y/norm, inv_now/norm, liability/norm, equity/norm, totalDebt/norm, asOfDate.strftime('%m/%y'), sep=' \t ')
