from flask import Flask, render_template, request
from flask_socketio import SocketIO
from yahooquery import Ticker

from yahooquery_cli import form_stock_list
from yahooquery_cli import get_ttm_ebitda_ocf, get_mrq_fin_strength, calc_rev_inv_stats 
from yahooquery_cli import get_q_rev_growth, get_yearly_revenue
from yahooquery_cli import get_mrq_gp_margin, get_ann_gp_margin
from yahooquery_cli import get_ev_to_rev, get_p_to_ocf


app = Flask(__name__)
socketio = SocketIO(app, async_mode='eventlet')
data = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/results', methods=['GET'])
def results():
    # Render the results page initially (no data yet)
    return render_template('results.html', data=[])

@app.route('/start_process', methods=['POST'])
def start_process():
    stock_from_UI = ''.join(request.form.getlist('stock'))
    stocks_list = form_stock_list(stock_from_UI)

    # Ensure stocks_list is a list
    if isinstance(stocks_list, str):
        stocks_list = stocks_list.split()  # Split by space if only one stock is given

    global data
    data.clear()  # Reset data for each new request

    # Process each stock and send updates
    for stockname in stocks_list:
        if stockname:
            stock = Ticker(stockname)
            fin_data = stock.financial_data.get(stockname, {})
            avg_inv_to_rev, inv_to_rev_mrq, remark_inv = calc_rev_inv_stats(stock)
            ebitda, ocf, tot_rev = get_ttm_ebitda_ocf(stock, fin_data)
            equity_ratio, net_debt, asOfDate = get_mrq_fin_strength(stock)
            q_rev_growth = get_q_rev_growth(fin_data)
            av_rev_growth, remark_rev = get_yearly_revenue(stock)
            mrq_gp_margin, mrq_ocf_margin, mrq_fcf_margin = get_mrq_gp_margin(stock)
            av_gp_margin, av_ocf_margin, av_fcf_margin = get_ann_gp_margin(stock)
            remarks = remark_rev + ' ' + remark_inv

            key_stats = stock.key_stats.get(stockname, {}) if stockname != 'bion.sw' else {}
            ev_to_rev = get_ev_to_rev(stock, key_stats)
            summary_detail = stock.summary_detail.get(stockname, {})
            p_to_ocf = get_p_to_ocf(summary_detail, ocf)

            stock_data = {
                'symbol': stockname,
                'equity_ratio': equity_ratio * 100,
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
            data.append(stock_data)
            socketio.emit('update_data', stock_data)  # Send each stock data line-by-line

    # Emit a 'process_complete' event to the client after all data is processed
    socketio.emit('process_complete')
    return '', 204  # Return empty response



# Replace app.run() with socketio.run(app)
if __name__ == '__main__':
    socketio.run(app, host="127.0.0.1", port=8000)