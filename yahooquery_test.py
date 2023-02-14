#import yahooquery as yq
from yahooquery import Ticker

norm = 1000000

for stockname in ['mo', 'amt', 'googl']:
    stock = Ticker(stockname)

#    print(stock.summary_detail)

    # get yearly-relevant data: Inventory and TotalRevenue
    types_yearly = ['Inventory', 'TotalRevenue']

    yearly_info = stock.get_financial_data(types_yearly, trailing = False).tail(2)

    rev_last_y, rev_now = yearly_info['TotalRevenue']

    while True: 
        try:
            inv_last_y, inv_now = yearly_info['Inventory']
            break
        except KeyError:
            inv_last_y = 0
            inv_now = 0
            break

    # get asset profile
    ebitda = stock.financial_data[stockname]['ebitda']

    # get TTM-relevant data

    types = ['CashAndCashEquivalents', 'TotalLiabilitiesNetMinorityInterest', 'TotalEquityGrossMinorityInterest', 'TotalDebt', 'OperatingCashFlow', 'FreeCashFlow']

    quartal_info = stock.get_financial_data(types, frequency='q', trailing=True)

#    print (quartal_info)

    cash = quartal_info['CashAndCashEquivalents'].iloc[-2]
    liability = quartal_info['TotalLiabilitiesNetMinorityInterest'].iloc[-2] 
    equity = quartal_info['TotalEquityGrossMinorityInterest'].iloc[-2]
    totalDebt = quartal_info['TotalDebt'].iloc[-2]
    asOfDate = quartal_info['asOfDate'].iloc[-2]

    print (rev_last_y/norm, rev_now/norm, ebitda/norm, cash/norm, inv_last_y/norm, inv_now/norm, liability/norm, equity/norm, totalDebt/norm, asOfDate.strftime('%m/%y'), sep=' \t ')

#    interest = quartal_info['InterestExpense']
#    d_and_a = quartal_info['DepreciationAndAmortization']
    ocf = quartal_info['OperatingCashFlow']
    fcf = quartal_info['FreeCashFlow']
