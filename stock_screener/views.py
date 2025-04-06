from flask import render_template, request
from flask_socketio import SocketIO

from . import app
from .crud import update_stock_data
from .yahooquery_cli import form_stock_list
from .utils import elapsed_time

socketio = SocketIO(app)


@app.route('/update')
def update_universe():
    pass


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/results', methods=['POST'])
def results():
    data = []

    # get the input from the UI form
    stock_key = request.form.get('stock_key')  # Get the selected stock key from the dropdown
    custom_ticker = request.form.get('custom_ticker')  # Get the custom ticker if provided

    # Determine which stock ticker to use
    if stock_key == 'custom' and custom_ticker:
        stock_from_UI = custom_ticker
    else:
        stock_from_UI = stock_key

    stocks_list = form_stock_list(stock_from_UI)

    print(stocks_list)

    for stockname in stocks_list:
        if stockname != '':
            updated_data = update_stock_data(stockname)
            data.append(updated_data)
            # print(stock_stats) # debugging
        else:
            data.append({})

        socketio.emit('update_data', data)
    return render_template('results.html', data=data)
