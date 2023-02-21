from yahooquery import Ticker
import numpy as np
import math
import sys
import argparse
from flask import Flask, request, render_template
from yahooquery import Ticker

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/results', methods=['POST'])
def results():
    stocks_list = request.form.getlist('stock')
    data = []

    for stockname in stocks_list:
        if stockname != '':

            stock = Ticker(stockname)

            av_inv_to_rev, inv_to_rev_mrq = calc_revenue_inventory_stats(stock)

            ebitda = get_ttm_ebitda(stock, stockname)

            equity_ratio, net_debt, asOfDate = get_mrq_financial_strength(stock)

            data.append({
                'name': stockname,
                'equity_ratio': "{:.0f}%".format(equity_ratio * 100),
                'net_debt': "{:.1f}".format(net_debt / ebitda),
                'av_inv_to_rev': "{:.0f}%".format(av_inv_to_rev * 100),
                'inv_to_rev_mrq': "{:.0f}%".format(inv_to_rev_mrq * 100),
                'asOfDate': asOfDate.strftime('%m/%y')
            })

    return render_template('results.html', data=data)


#def main():
#
#    # Initialize parser
#    parser = argparse.ArgumentParser()
#
#    # Passing a shortname of a stockslist (or stock symbols)
#    listarg = []
#    parser.add_argument("-l", nargs="*", help = "Stocks list name: div, growth, rest, watch, watchgrow, watchcomm or stock symbol")
#    args = parser.parse_args()
#    listarg = args.l
#   
#    # Fill in a list of stocks based on the input option 
#    stocks_list = []
#
#    if listarg[0] == "div":
#        stocks_list = ['abbv', 'alv.de', 'mo', 'amt', 'amgn', 'ay', 'bti', 'blk', 'bepc', 'csco', 'dlr', 'enb', 'ecv.de', 
#        'hei.de', 'ibe.mc', 'intc', 'irm', 'kmi', '8001.t', 'lvmhf', 'mpw', '4091.t', 'ohi', 'spg', 'swa.de', 'swk', 'ul']
#    elif listarg[0] == "growth":
#        stocks_list = ['adbe', 'abnb', 'googl', 'amzn', 'asml', 'bntx', 'sq', 'coin', 'c0m.de', 'hyq.de', 'ma', 'meta', 'pltr', 'veev']
#    elif listarg[0] == "rest":
#        stocks_list = ['eqnr', 'rio', 'arcc', 'ocsl']
#    elif listarg[0] == "watch":
#        stocks_list = ['tte', 'shel', '', '', 'apd', 'lin', 'bas.de', '', '', 'mmm', 'dpw.de', 'fra.de', 'ge', 'hot.de', 'lmt', 'raa.de', 
#                '', '', 'mcd', 'ads.de', 'prx.as', 'sbux', 'vfc', '', '', '2502.t', 'ko', 'k', 'nesn.sw', 'pep', 'pm', '', '',
#                'bayn.de', 'bion.sw', 'bmy', 'gild', 'jnj', 'nvs', 'rog.sw', 'soon.sw', '', '', 'brk-b', 'ms', 'muv2.de', '', '',
#                '4901.t', 'ibm', 'msft', 'txn', '', '', 't', 'dte.de', 'dis', 'vz', '', '', 'bipc', 'ibe.mc', 'red.mc', '', '',
#                'amt', 'avb', 'dkg.de', 'dea', 'krc', 'nnn', 'stag', 'skt', 'vici', 'vna.de', 'wpc']
#    elif listarg[0] == "watchgrow":
#        stocks_list = ['bkng', 'bidu', 'cdr.wa', 'crwd', 'splk', 'baba', 'tdoc', 'tcehy', 'tsla', 'twlo', 'pton', 'upst', 'vmeo',
#                'isrg', '6060.hk', 'aapl', 'nem.de', 'nvda', 'var1.de', 'estc', 'hfg.de', 'qlys', 'pypl', 'zal.de', 'zm']
#    elif listarg[0] == "watchcomm":
#        stocks_list = ['eog']
#    else:
#        stocks_list = listarg
#
#    # Get stats for the stocks in the list
#    for stockname in stocks_list:
#        if stockname != '':
#
#            stock = Ticker(stockname)
#
#            av_inv_to_rev, inv_to_rev_mrq = calc_revenue_inventory_stats(stock)
#
#            ebitda = get_ttm_ebitda(stock, stockname)
#           
#            equity_ratio, net_debt, asOfDate = get_mrq_financial_strength(stock)
#
#            print ("{} \t {:5.0f}% \t {:4.1f} \t {:5.0f}% \t {:5.0f}%".format(
#                    stockname, 
#                    equity_ratio * 100, net_debt / ebitda,
#                    av_inv_to_rev * 100, inv_to_rev_mrq * 100), 
#                    asOfDate.strftime('%m/%y'), sep=' \t ')
#
#        #    norm = 1000000
#        #    print (stockname, tot_rev/norm, ebitda/norm, cash/norm, 
#        #            "{:,.2f}%".format(av_inv_to_rev*100), "{:,.2f}%".format(inv_to_rev_mrq*100), 
#        #            liability/norm, equity/norm, totalDebt/norm, asOfDate.strftime('%m/%y'), sep=' \t ')
#
#        else:
#            print(' ')


#***********************************************
#****   get ttm ebitda from asset profile   ****
#***********************************************
def get_ttm_ebitda(_stock, _stockname):

    while True:
        try:
            _ebitda = _stock.financial_data[_stockname]['ebitda']
            break
        except KeyError:
            _ebitda = 0.
            break
        except KeyValue:
            _ebitda = 0.
            break

    return _ebitda
    pass


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
    pass


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
    pass

if __name__ == '__main__':
    app.run(debug=True, port=5008)
#if __name__ == "__main__":
#    main()
