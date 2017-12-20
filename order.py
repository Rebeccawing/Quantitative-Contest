from GlobalPramaters import *
from Global import *
import utils

# 开多仓：BID LONG
# 平多仓：ASK LONG
# 开空仓：ASK SHORT
# 平多仓：BID SHORT

class Order:
    def __init__(self):
        self.buf = []

    def insert_order(self, side, symbol, volume, price, is_market, pos_type):
        self.buf.append((side,symbol,volume,price,is_market,pos_type))

    def insert_sellLongSlow(self, symbol, volume, price, is_market):
        self.buf.append((common_pb2.ASK, symbol, volume, price, is_market, common_pb2.LONG))

    def insert_openLongPosition(self, symbol, volume, price, is_market):
        self.buf.append((common_pb2.BID, symbol, volume, price, is_market, common_pb2.LONG))

    def insert_openShortPosition(self,symbol, volume, price, is_market):
        self.buf.append((common_pb2.ASK, symbol, volume, price, is_market, common_pb2.SHORT))

    def insert_closePosition(self,symbol):
        positions = utils.get_trader(common_pb2.FULL_INFO).positions
        if hasattr(positions, 'long_positions'):
            long_positions = positions.long_positions
            if long_positions[symbol] is not None:
                self.buf.append((common_pb2.ASK, symbol, long_positions[symbol].volume, None,
                                 True, common_pb2.LONG))
        if hasattr(positions, 'short_positions'):
            short_positions = positions.short_positions
            if short_positions[symbol] is not None:
                self.buf.append((common_pb2.BID, symbol, short_positions[symbol].volume, None,
                                True, common_pb2.SHORT))


    def execute(self):
        for order in self.buf:
            utils.new_order(common_pb2.NEW_ORDER, None, order[0],order[1],order[2],order[3],order[4],order[5])
        self.buf = []


