from pprint import pprint
from datetime import datetime
import requests
from lxml import etree
import grpc

from institutions.utils import get_grpc_hostname
from api.protos import database_pb2_grpc
from api.protos.database_pb2 import BoughtOrSold
from api.protos.protobuf_datatype_utils import datetime_to_timestamp

class InstitutionsParser():

    def __init__(self):

        channel = grpc.insecure_channel(f'{get_grpc_hostname()}:6565')
        self.stub = database_pb2_grpc.DatabaseStub(channel)

        self.max_count = 12
        self.url = 'https://www.cnyes.com/twstock/a_institutional7.aspx'
        self.symbol_xpath = "//*[contains(@class, 'fLtBx')]//tbody//tr//td[1]//a"
        self.foreign_xpath = "//*[contains(@class, 'fLtBx')]//tbody//tr//td[3]"
        self.quantity_xpath = "//*[contains(@class, 'fLtBx')]//tbody//tr//td[6]"
        self.dict = {}
        self.date_xpath = "//*[contains(@class, 'tydate')]"
        self.date = None
        self.model = 'twse_over_bought'

    def exclude_condition(self, input):
        if input <= 0:
            return True
        else:
            return False

    def parse(self):
        print(f'==> parse page: {self.url}')
        resp = requests.get(self.url, timeout=60)
        resp.raise_for_status()
        content = resp.text
        tree = etree.HTML(content)

        self.date = datetime.strptime(tree.xpath(self.date_xpath)[0].text.strip(), '%Y-%m-%d')
        print(self.date)
        symbols = tree.xpath(self.symbol_xpath)
        foreigns = tree.xpath(self.foreign_xpath)
        quantities = tree.xpath(self.quantity_xpath)
        self.dict = {}
        for symbol, foreign, quantity in zip(symbols, foreigns, quantities):
            if len(self.dict) >= self.max_count:
                break
            elif self.exclude_condition(int(foreign.text.strip())):
                continue
            else:
                self.dict[symbol.text.strip()] = int(quantity.text.strip())
        pprint(self.dict)
        return self

    def save_to_db(self):

        for key, value in self.dict.items():
            _dict = {
                'symbol': key,
                'date': datetime_to_timestamp(self.date),
                'quantity': value
            }
            try:
                if self.model == 'twse_over_bought':
                    rowcount = self.stub.insert_twse_over_bought(BoughtOrSold(
                        symbol=_dict['symbol'],
                        date=_dict['date'],
                        quantity=_dict['quantity']
                    ))
                    print(rowcount)
                elif self.model == 'twse_over_sold':
                    rowcount = self.stub.insert_twse_over_sold(BoughtOrSold(
                        symbol=_dict['symbol'],
                        date=_dict['date'],
                        quantity=_dict['quantity']
                    ))
                    print(rowcount)
                else:
                    raise Exception(f'unsupported model type: {self.model}')
            except grpc.RpcError as e:
                status_code = e.code()
                print(e.details())
                print(status_code.name, status_code.value)
