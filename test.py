import requests
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from bs4 import BeautifulSoup
import re
from datetime import datetime
from time import mktime

def _get_crumbs_and_cookies(stock):

#    url = 'https://finance.yahoo.com/quote/{}/financials'.format(stock)
    url = 'https://seekingalpha.com/symbol/{}/income-statement'.format(stock)
    print (url)

    options = Options()
    options.headless = True
    options.add_argument("--window-size=1920,1200")

    driver = webdriver.Firefox()

    website = driver.get(url)

def main():
    stock = 'ABBV'

    _get_crumbs_and_cookies(stock)


if __name__ == "__main__":
    main()

