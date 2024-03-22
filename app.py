from flask import Flask, request, render_template
from yahooquery import Ticker
import numpy as np
import math
import datetime
from yahooquery_cli import form_stock_list
from yahooquery_cli import get_ttm_ebitda_ocf, get_mrq_financial_strength, calc_revenue_inventory_stats 

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/results', methods=['POST'])
def results():
    stock_string = ''.join(form_stock_list(request.form.getlist('stock'))) 
    print(stock_string)
    stocks_list = form_stock_list(stock_string)
    print(stocks_list)
    data = []

    for stockname in stocks_list:
        if stockname != '':

            stock = Ticker(stockname)
            fin_data = stock.financial_data[stockname]

            avg_inv_to_rev, inv_to_rev_mrq, remark = calc_revenue_inventory_stats(stock)

            ebitda, ocf, tot_rev = get_ttm_ebitda_ocf(stock, fin_data)

            equity_ratio, net_debt, asOfDate = get_mrq_financial_strength(stock)

            data.append({
                'symbol': stockname,
                'equity_ratio': equity_ratio * 100,
                'ndebt_to_ebitda': equity_ratio * 100,
                'net_debt_ebitda': net_debt / ebitda,
                'inv_to_rev_mrq': inv_to_rev_mrq * 100,
                'avg_inv_to_rev': avg_inv_to_rev * 100,
                'as_of_date': asOfDate.strftime('%m/%y')
            })

    return render_template('results.html', data=data)

if __name__ == '__main__':
    app.run(debug=True, port=5008)
