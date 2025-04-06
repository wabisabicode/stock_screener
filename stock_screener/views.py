from datetime import datetime

from flask import render_template, request
from flask_socketio import SocketIO
from yahooquery import Ticker


from . import app
from .yahooquery_cli import (calc_rev_inv_stats, form_stock_list,
                             get_ann_gp_margin, get_ev_to_rev,
                             get_mrq_fin_strength, get_mrq_gp_margin,
                             get_p_to_ocf, get_q_rev_growth,
                             get_ttm_ebitda_ocf, get_yearly_revenue)
from .utils import elapsed_time

socketio = SocketIO(app)

data = []


@app.route('/update')
def update_universe():
    pass


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/results', methods=['POST'])
def results():
    time_start = datetime.now()

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

    time_list_formed = elapsed_time(time_start, 'List formed in')

    for stockname in stocks_list:
        if stockname != '':
            time_start_anal = datetime.now()

            stock = Ticker(stockname)
            fin_data = stock.financial_data[stockname]
            time_got_fin_data = elapsed_time(time_start_anal, 'Got fin_data in')

            avg_inv_to_rev, inv_to_rev_mrq, remark_inv = calc_rev_inv_stats(stock)
            time_calc_rev_inv = elapsed_time(time_got_fin_data, 'Calc rev inv in')

            ebitda, ocf, tot_rev = get_ttm_ebitda_ocf(stock, fin_data)
            time_got_ttm_ebitda_ocf = elapsed_time(time_calc_rev_inv, 'Got ebitda, ocf in')

            equity_ratio, net_debt, asOfDate = get_mrq_fin_strength(stock)
            time_got_fin_strength = elapsed_time(time_got_ttm_ebitda_ocf, 'Got fin strength in')

            q_rev_growth = get_q_rev_growth(fin_data)
            av_rev_growth, remark_rev = get_yearly_revenue(stock)
            time_got_rev_growth = elapsed_time(time_got_fin_strength, 'Got rev growth in')

            mrq_gp_margin, mrq_ocf_margin, mrq_fcf_margin = get_mrq_gp_margin(stock)
            time_got_mrq_margins = elapsed_time(time_got_rev_growth, 'Got mrq margins in')

            av_gp_margin, av_ocf_margin, av_fcf_margin = get_ann_gp_margin(stock)
            time_got_av_margins = elapsed_time(time_got_mrq_margins, 'Got av margins in')

            remarks = remark_rev + ' ' + remark_inv

            # get current valuations for EV-to-Rev and Price/OCF
            if stockname != 'bion.sw':
                key_stats = stock.key_stats[stockname]
            else:
                key_stats = 0
            
            ev_to_rev = get_ev_to_rev(stock, key_stats)

            summary_detail = stock.summary_detail[stockname]
            p_to_ocf = get_p_to_ocf(summary_detail, ocf)

            time_got_valuations = elapsed_time(time_got_av_margins, 'Got valuations in')
            print('------')
            time_total = elapsed_time(time_start_anal, 'Got valuations in')
            print('')

            stock_stats = {
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
            }
            data.append(stock_stats)
            # print(stock_stats) # debugging
        else:
            data.append({})

        socketio.emit('update_data', data)
    return render_template('results.html', data=data)
