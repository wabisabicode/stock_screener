from flask import Flask, request, render_template
from yahooquery import Ticker
import numpy as np
import math
import datetime
from yahooquery_cli import form_stock_list
from yahooquery_cli import get_ttm_ebitda_ocf, get_mrq_financial_strength, calc_revenue_inventory_stats 
from yahooquery_cli import get_q_rev_growth, get_yearly_revenue
from yahooquery_cli import get_mrq_gp_margin, get_yearly_gp_margin

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/results', methods=['POST'])
def results():

    # get the input from the UI form
    stock_from_UI = ''.join(request.form.getlist('stock'))

    stocks_list = form_stock_list(stock_from_UI)

    # check if stocks_list is a string (only a selected stock is desired)
    if type(stocks_list) is str:
        stocks_list = stocks_list.split() # splits the stockname by ' ' instead of letters

    data = []

    for stockname in stocks_list:
        if stockname != '':

            stock = Ticker(stockname)
            fin_data = stock.financial_data[stockname]

            avg_inv_to_rev, inv_to_rev_mrq, remark_inv = calc_revenue_inventory_stats(stock)

            ebitda, ocf, tot_rev = get_ttm_ebitda_ocf(stock, fin_data)

            equity_ratio, net_debt, asOfDate = get_mrq_financial_strength(stock)

            q_rev_growth = get_q_rev_growth(fin_data)
            av_rev_growth, remark_rev = get_yearly_revenue(stock)

            mrq_gp_margin, mrq_ocf_margin, mrq_fcf_margin = get_mrq_gp_margin(stock)
            av_gp_margin, av_ocf_margin, av_fcf_margin = get_yearly_gp_margin(stock)

            data.append({
                'symbol': stockname,
                'equity_ratio': equity_ratio * 100,
                'ndebt_to_ebitda': equity_ratio * 100,
                'net_debt_ebitda': net_debt / ebitda,
                'inv_to_rev_mrq': inv_to_rev_mrq * 100,
                'avg_inv_to_rev': avg_inv_to_rev * 100,
                'q_rev_growth_ui': q_rev_growth * 100,
                'av_rev_growth_ui': av_rev_growth * 100 - 100,
                'mrq_gp_margin_ui': mrq_gp_margin * 100, 
                'av_gp_margin_ui': av_gp_margin * 100,
                'mrq_ocf_margin_ui': mrq_ocf_margin * 100, 
                'av_ocf_margin_ui': av_ocf_margin * 100,
                'mrq_fcf_margin_ui': mrq_fcf_margin * 100, 
                'av_fcf_margin_ui': av_fcf_margin * 100,
                'as_of_date': asOfDate.strftime('%m/%y')
            })

    return render_template('results.html', data=data)

if __name__ == '__main__':
    app.run(debug=True, port=5008)
