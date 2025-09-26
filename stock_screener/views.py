from flask import Blueprint, render_template, request

from .crud import update_stock_data
from .yahooquery_cli import form_stock_list

main = Blueprint('main', __name__)


@main.route('/update')
def update_universe():
    pass


@main.route('/')
def home():
    return render_template('home.html')


@main.route('/results', methods=['POST'])
def results():
    data = []

    # get the input from the UI form
    stock_key = request.form.get('stock_key')
    custom_ticker = request.form.get('custom_ticker')

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
            # print(updated_data) # debugging
        else:
            data.append({})

    return render_template('results.html', data=data)
