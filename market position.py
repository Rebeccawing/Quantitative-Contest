from GlobalPramaters import *
from Global import *
import utils


class MarketPosition:
    def __init__(self):
        self.marketPosition = {}
        self.averageEntryPrice = {}
        self.unrealizedPnl = {}

        for symbol in SYMBOLS:
            self.marketPosition[symbol] = 0
            self.averageEntryPrice[symbol] = 0
            self.unrealizedPnl[symbol] = 0


    def renew_all_market_position(self):
        positions = utils.get_trader(common_pb2.FULL_INFO).positions
        for symbol in SYMBOLS:
            market_position = 0
            avg_entry_price = 0
            unrealized_pnl = 0

            if hasattr(positions, 'long_positions') and positions.long_positions[symbol] is not None:
                if hasattr(positions.long_positions[symbol], 'volume'):
                    if positions.long_positions[symbol].volume > 0:
                        market_position = positions.long_positions[symbol].volume
                        avg_entry_price = positions.long_positions[symbol].avg_price
                        unrealized_pnl = positions.long_positions[symbol].unrealized_pnl

            if hasattr(positions, 'short_positions') and positions.short_positions[symbol] is not None:
                if hasattr(positions.short_positions[symbol], 'volume'):
                    if positions.short_positions[symbol].volume > 0:
                        market_position = - positions.short_positions[symbol].volume
                        avg_entry_price = positions.short_positions[symbol].avg_price
                        unrealized_pnl = positions.short_positions[symbol].unrealized_pnl

            self.marketPosition[symbol] = market_position
            self.averageEntryPrice[symbol] = avg_entry_price
            self.unrealizedPnl[symbol] = unrealized_pnl
        return self.marketPosition


