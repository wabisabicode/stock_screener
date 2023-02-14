#import yahooquery as yq
from yahooquery import Ticker

stock = Ticker('abbv')

print(stock.summary_detail)

print(stock.income_statement(frequency='q')['EBITDA'])

print(stock.balance_sheet(frequency='q'))

print(stock.cash_flow(frequency='q'))
