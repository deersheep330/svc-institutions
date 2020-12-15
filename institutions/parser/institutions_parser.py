from pprint import pprint
from datetime import datetime

import requests
from lxml import etree

class InstitutionsParser():

    def __init__(self):
        self.url = 'https://www.cnyes.com/twstock/a_institutional8.aspx'
        self.symbol_xpath = "//*[contains(@class, 'fLtBx')]//tbody//tr//td[1]//a"
        self.foreign_xpath = "//*[contains(@class, 'fLtBx')]//tbody//tr//td[3]"
        self.quantity_xpath = "//*[contains(@class, 'fLtBx')]//tbody//tr//td[6]"
        self.dict = {}
        self.date_xpath = "//*[contains(@class, 'tydate')]"
        self.date = None

    def exclude_condition(self, input):
        if input <= 0:
            return True
        else:
            return False

    def parse(self):
        print(f'==> parse page: {self.url}')
        resp = requests.get(self.url)
        content = resp.text
        tree = etree.HTML(content)

        self.date = datetime.strptime(tree.xpath(self.date_xpath)[0].text.strip(), '%Y-%m-%d')
        print(self.date)
        symbols = tree.xpath(self.symbol_xpath)
        foreigns = tree.xpath(self.foreign_xpath)
        quantities = tree.xpath(self.quantity_xpath)
        self.dict = {}
        for symbol, foreign, quantity in zip(symbols, foreigns, quantities):
            if len(self.dict) >= 10:
                break
            elif self.exclude_condition(int(foreign.text.strip())):
                continue
            else:
                self.dict[symbol.text.strip()] = int(quantity.text.strip())
        pprint(self.dict)

    def save_to_db(self):
        pass