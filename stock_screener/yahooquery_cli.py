import argparse

from .crud import update_stock_data


def form_stock_list(_listarg):
    # Mapping list options to specific stock lists
    stock_options = {
        "div": [
            'abbv', 'are', 'alv.de', 'mo', 'bats.l', 'blk', 'bepc',
            'enb', 'ibe.mc', 'kmi', '8001.t', 'lvmhf', 'mpw', '4091.t',
            'nnn', 'novo-b.co', 'ohi', 'pfe', 'spg', 'six3.f', 'vna.de'
        ],

        "growth": [
            'adbe', 'abnb', 'googl', 'amzn', 'asml', 'bntx', 'xyz', 'net',
            'coin', 'dis', 'gtlb', 'hyq.de', 'ma', 'twlo', 'veev', 'vmeo'
        ],

        "rest": ['eqnr', '', 'rio.l', '', '', 'arcc', 'ocsl'],

        "watch": [
            'tte', 'shel', '', '', 'apd', 'hei.de', 'lin', 'bas.de', '', '',
            'mmm', '6367.t', 'dhl.de', 'fra.de',
            'ge', 'hot.de', 'raa.de', 'swk', '', '',
            'ads.de', 'mcd', 'nke', 'sbux', 'vfc', '', '',
            '2502.t', 'ko', 'dge.l', 'nlm.f', 'hsy', 'k', 'mdlz', 'nesn.sw',
            'pep', 'pm', 'swa.de', 'ul', '', '',
            'amgn', 'bayn.de', 'bion.sw', 'bmy', 'cvs', 'gild',
            'jnj', 'nvs', 'rog.sw', 'soon.sw', '', '',
            'brk-b', 'fih-u.to', 'itm.mi', 'ms', 'muv2.de', '', '',
            'bc8.f', 'csco', 'dell', '4901.t', 'hpq',
            'ibm', 'intc', 'meta', 'msft', 'txn', '', '',
            't', 'dte.de', 'iac', 'g24.de', 'vz', 'wbd', '', '',
            'bipc', 'nee', 'red.mc', '', '',
            'amt', 'avb', 'dlr', 'irm', 'dea', 'hr',
            'krc', 'o', 'stag', 'skt', 'vici', 'wpc'
        ],

        "watchgrow": [
            'aapl', 'bkng', 'crwd', 'estc',
            'hfg.de', 'isrg', 'lyft', 'mndy', 'nem.de', 'nvda', 'pltr', 'pypl', 'pton', 'qlys',
            'tmv.de', 'tdoc', 'tsla', 'uber',
            'zal.de', 'zm'
        ],

        "watchcomm": ['eog']
    }

    return stock_options.get(_listarg, [_listarg])


def display_table_header():
    print("     \t  | debt health |   inv-to-Rev\t| Rev Growth    |"
          " Gross Margin  | Free CashFlow |"
          "\t    \t    |  Valuation\t \t \t \t      | Dividend")
    print("stock\t    eqR\tnebitda\t i/Rmrq\t aIn/R\t qRGrYoY  aRGrY "
          "  mrqGM   avGMy   mrqFCF   avFCF   mrq"
          "\t Remark \tEV/Sale\t 4YEV/Sale\tEV/FCF\t 4Y EV/FCF"
          "\t DivY \t 5YDivY\t DivFwd\t Payout")
