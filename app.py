from flask import Flask, request, render_template
from yahooquery import Ticker
import numpy as np
import math
import datetime
from yahooquery_cli import get_ttm_ebitda, get_mrq_financial_strength, calc_revenue_inventory_stats 

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

            avg_inv_to_rev, inv_to_rev_mrq = calc_revenue_inventory_stats(stock)

            ebitda = get_ttm_ebitda(stock, stockname)

            equity_ratio, net_debt, asOfDate = get_mrq_financial_strength(stock)

            data.append({
                'symbol': stockname,
                'equity_ratio': equity_ratio * 100,
                'net_debt_ebitda': net_debt / ebitda,
                'avg_inv_to_rev': avg_inv_to_rev * 100,
                'inv_to_rev_mrq': inv_to_rev_mrq * 100,
                'as_of_date': asOfDate.strftime('%m/%y')
            })

    return render_template('results.html', data=data)

if __name__ == '__main__':
    app.run(debug=True, port=5008)
