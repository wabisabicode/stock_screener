import argparse

from .crud import update_stock_data


def display_table_header():
    print("     \t  | debt health |   inv-to-Rev\t| Rev Growth    |"
          " Gross Margin  | Free CashFlow |"
          "\t    \t    |  Valuation\t \t \t \t      | Dividend")
    print("stock\t    eqR\tnebitda\t i/Rmrq\t aIn/R\t qRGrYoY  aRGrY "
          "  mrqGM   avGMy   mrqFCF   avFCF   mrq"
          "\t Remark \tEV/Sale\t 4YEV/Sale\tEV/FCF\t 4Y EV/FCF"
          "\t DivY \t 5YDivY\t DivFwd\t Payout")
