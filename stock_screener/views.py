from flask import Flask, request, render_template
from flask_socketio import SocketIO
from yahooquery import Ticker
from .yahooquery_cli import form_stock_list
from .yahooquery_cli import get_ttm_ebitda_ocf, get_mrq_fin_strength, calc_rev_inv_stats 
from .yahooquery_cli import get_q_rev_growth, get_yearly_revenue
from .yahooquery_cli import get_mrq_gp_margin, get_ann_gp_margin
from .yahooquery_cli import get_ev_to_rev, get_p_to_ocf

from . import app

socketio = SocketIO(app)

data = []

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/results', methods=['POST'])
def results():

    # get the input from the UI form
    stock_key = request.form.get('stock_key')  # Get the selected stock key from the dropdown
    custom_ticker = request.form.get('custom_ticker')  # Get the custom ticker if provided

    print(stock_key)
    # Determine which stock ticker to use
    if stock_key == 'custom' and custom_ticker:
        stock_from_UI = custom_ticker  # Use the custom ticker
    else:
        stock_from_UI = stock_key  # Use the selected stock key

    stocks_list = form_stock_list(stock_from_UI)

    print(stocks_list)
    # check if stocks_list is a string (only a selected stock is desired)
    if type(stocks_list) is str:
        stocks_list = stocks_list.split()  # splits the stockname by ' ' instead of letters

    global data

    for stockname in stocks_list:
        if stockname != '':

            stock = Ticker(stockname)
            fin_data = stock.financial_data[stockname]

            avg_inv_to_rev, inv_to_rev_mrq, remark_inv = calc_rev_inv_stats(stock)

            ebitda, ocf, tot_rev = get_ttm_ebitda_ocf(stock, fin_data)

            equity_ratio, net_debt, asOfDate = get_mrq_fin_strength(stock)

            q_rev_growth = get_q_rev_growth(fin_data)
            av_rev_growth, remark_rev = get_yearly_revenue(stock)

            mrq_gp_margin, mrq_ocf_margin, mrq_fcf_margin = get_mrq_gp_margin(stock)
            av_gp_margin, av_ocf_margin, av_fcf_margin = get_ann_gp_margin(stock)

            remarks = remark_rev + ' ' + remark_inv

            # get current valuations for EV-to-Rev and Price/OCF
            if stockname != 'bion.sw':
                key_stats = stock.key_stats[stockname]
            else:
                key_stats = 0
            ev_to_rev = get_ev_to_rev(stock, key_stats)

            summary_detail = stock.summary_detail[stockname]
            p_to_ocf = get_p_to_ocf(summary_detail, ocf)

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
                'as_of_date': asOfDate.strftime('%m/%y'),
                'remarks_ui': remarks,
                'ev_to_rev_ui': ev_to_rev,
                'p_to_ocf_ui': p_to_ocf
            })
        else:
            data.append({})

        # print(data) # debugging
        socketio.emit('update_data', data)
    return render_template('results.html', data=data)
