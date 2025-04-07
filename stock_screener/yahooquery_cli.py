import argparse

from .crud import update_stock_data


def main():
    display_table_header()

    # Initialize parser
    parser = argparse.ArgumentParser()

    # Passing a shortname of a stockslist (or stock symbols)
    listarg = []
    parser.add_argument("-l", nargs="*",
                        help=("Stocks list name: div, growth, rest, watch,"
                              "watchgrow, watchcomm or stock symbol"))
    args = parser.parse_args()
    listarg = args.l

    stocks_list = form_stock_list(listarg[0])

    # Get stats for the stocks in the list
    for stockname in stocks_list:
        if stockname != '':
            stock_data = update_stock_data(stockname)

            print(
                "{}\t ".format(stockname),
                "{:4.0f}%\t{:5.1f} \t".format(
                    stock_data['equity_ratio'], stock_data['net_debt_to_ebitda']),
                " {:3.0f}% \t {:3.0f}% \t\t".format(
                    stock_data['inv_to_rev_mrq'], stock_data['av_inv_to_rev']),
                "{:3.0f}% \t {:3.0f}% \t".format(
                    stock_data['q_rev_growth'], stock_data['av_rev_growth']),
                "{:4.0f}% \t {:4.0f}% \t".format(
                    stock_data['mrq_gp_margin'], stock_data['av_gp_margin']),
                "{:4.0f}% \t {:4.0f}% \t".format(
                    stock_data['mrq_ocf_margin'], stock_data['av_ocf_margin']),
                "{:4.0f}% \t {:4.0f}% \t".format(
                    stock_data['mrq_fcf_margin'], stock_data['av_fcf_margin']),
                stock_data['as_of_date'],
                "\t{}\t\t".format(stock_data['remarks']),
                "{:5.2f}\t{:6.2f}".format(
                    stock_data['ev_to_rev'],
                    stock_data['p_to_ocf']
                )
            )
        else:
            print(' ')


def form_stock_list(_listarg):
    # Mapping list options to specific stock lists
    stock_options = {
        "div": [
            'abbv', 'are', 'alv.de', 'mo', 'amt', 'bti', 'blk', 'bepc',
            'enb', 'ibe.mc', 'kmi', '8001.t', 'lvmhf',
            'mpw', '4091.t', 'nnn', 'ohi', 'pfe', 'spg', 'vna.de'
        ],

        "growth": [
            'adbe', 'abnb', 'googl', 'amzn', 'asml', 'bntx', 'xyz', 'net',
            'coin', 'dis', 'gtlb', 'hyq.de', 'ma', 'twlo', 'veev', 'vmeo'
        ],

        "rest": ['eqnr', '', 'rio', '', '', 'arcc', 'ocsl'],

        "watch": [
            'tte', 'shel', '', '', 'apd', 'hei.de', 'lin', 'bas.de', '', '',
            'mmm', '6367.t', 'dhl.de', 'fra.de',
            'ge', 'hot.de', 'raa.de', 'swk', '', '',
            'ads.de', 'mcd', 'nke', 'sbux', 'vfc', '', '',
            '2502.t', 'ko', 'k', 'nesn.sw', 'pep',
            'pm', 'swa.de', 'ul', '', '',
            'amgn', 'bayn.de', 'bion.sw', 'bmy', 'cvs', 'gild',
            'jnj', 'nvs', 'nvo', 'rog.sw', 'soon.sw', '', '',
            'brk-b', 'ms', 'muv2.de', '', '',
            'csco', 'dell', '4901.t', 'hpq',
            'ibm', 'intc', 'meta', 'msft', 'txn', '', '',
            't', 'dte.de', 'iac', 'g24.de', 'vz', 'wbd', '', '',
            'bipc', 'nee', 'red.mc', '', '',
            'avb', 'dlr', 'irm', 'dea', 'hr',
            'krc', 'o', 'stag', 'skt', 'vici', 'wpc'
        ],

        "watchgrow": [
            'aapl', 'bkng', 'crwd', 'estc',
            'hfg.de', 'isrg', 'nem.de', 'nvda', 'pltr', 'pypl', 'pton', 'qlys',
            'tmv.de', 'tdoc', 'tsla', 'uber',
            'zal.de', 'zm'
        ],

        "watchcomm": ['eog']
    }

    return stock_options.get(_listarg, [_listarg])


def display_table_header():
    print("     \t  | debt health |   inv-to-Rev\t |\tRev Growth     |"
          " Gross Margin  |  Op CashFlow  | Free CashFlow |"
          "\t    \t     \t  |       Valuation\t")
    print("stock\t    eqR\tnebitda\t i/Rmrq\t aIn/R\t\tqRGrYoY\t aRGrY "
          "\t mrqGM \t avGMy \t mrqOCF\t avOCFy\t mrqFCF\t avFCFy\t mrq"
          "\t Remark \t\tEV/Sale\t P/OCF")


if __name__ == "__main__":
    main()
