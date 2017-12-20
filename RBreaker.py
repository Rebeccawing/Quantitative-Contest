from GlobalPramaters import *
from Global import *
import Data_processing


class R_Breaker(Data_processing.Strategies):
    """
    观察卖出价 = 最高价 + 0.35*（收盘价 - 最低价）； k1
    观察买入价 = 最低价 - 0.35*（最高价 - 收盘价）；
    反转卖出价 = 1.07/2*（最高价 + 最低价） - 0.07*最低价； k2 k3
    反转买入价 = 1.07/2*（最高价 + 最低价） - 0.07*最高价；
    突破买入价 = 观察卖出价 + 0.25*（观察卖出价 – 观察买入价）； k4
    突破卖出价 = 观察买入价 – 0.25*（观察卖出价 – 观察买入价）。
    """

    def __init__(self,symbol, Run_freq, data_freq, gap = 0.1, trade_shares = 1, k1 = 0.35, k2=1.07, k3 =0.07, k4=0.25):
        super(R_Breaker, self).__init__()
        self.k1 = k1
        self.k2 = k2
        self.k3 = k3
        self.k4 = k4
        self.Run_freq = Run_freq
        self.data_freq =data_freq
        self.gap = gap
        self.counter = -1
        self.ObserSellThr = None
        self.trade_shares = trade_shares
        self.symbol = symbol

    @property
    def Open(self):
        return self.PriceList[-int(self.data_freq/self.gap)]

    @property
    def High(self):
        return max(self.PriceList[-int(self.data_freq/self.gap):])

    @property
    def Low(self):
        return min(self.PriceList[-int(self.data_freq/self.gap):])

    @property
    def Close(self):
        return self.PriceList[-1]

    def cal_thr(self):
        self.ObserSellThr = self.High + self.k1 * (self.Close - self.Low)
        self.ObserBuyThr = self.Low - self.k1 * (self.High - self.Close)
        self.RevertSellThr = self.k2/2 * (self.High +self.Low) -  self.k3 * self.Low
        self.RevertBuyThr = self.k2/2 * (self.High + self.Low) - self.k3 * self.High
        self.BreakBuyThr = self.ObserSellThr + self.k4 * (self.ObserSellThr - self.ObserBuyThr)
        self.BreakSellThr = self.ObserBuyThr - self.k4 * (self.ObserSellThr - self.ObserBuyThr)
        self.isCrossObserSellThr = False
        self.isCrossObserBuyThr = False


    def run(self):
        self.counter = self.counter + 1
        if self.counter >= self.data_freq / self.Run_freq:
            self.cal_thr()
            self.counter = 0
        if self.ObserSellThr is None:
            return

        trade_flag = 0

        last_price = self.PriceList[-1]
        if marketPosition.marketPosition[self.symbol] == 0:
            if last_price < self.BreakSellThr:
                trade_flag = -1
                #order.insert_openShortPosition(symbol=self.symbol,volume=self.trade_shares, price=None, is_market=True)
                #空仓情况下，盘中价格跌破突破卖出价，采取趋势策略，即在该点做空；
            if last_price > self.BreakBuyThr:
                trade_flag = 1
                #order.insert_openLongPosition(symbol=self.symbol,volume=self.trade_shares, price=None, is_market=True)
                #空仓情况下，盘中价格超过突破买入价，采取趋势策略，即在该点做多


        if last_price > self.ObserSellThr:
            self.isCrossObserSellThr = True
        if last_price < self.ObserBuyThr:
            self.isCrossObserBuyThr = True

        if marketPosition.marketPosition[self.symbol] > 0 and self.isCrossObserSellThr:
            if last_price < self.RevertSellThr:
                trade_flag = -1
                #order.insert_closePosition(self.symbol)
                #order.insert_openShortPosition(symbol=self.symbol, volume=self.trade_shares, price=None, is_market=True)
                #持多单时，当日最高价超过观察卖出价后，盘中价格回落且跌破反转卖出价，采取 反转策略，即在该点位反手做空；
        if marketPosition.marketPosition[self.symbol] < 0 and self.isCrossObserBuyThr:
            if last_price > self.RevertBuyThr:
                trade_flag = 1
                #order.insert_closePosition(self.symbol)
                #order.insert_openLongPosition(symbol=self.symbol,volume=self.trade_shares, price=None, is_market=True)
                #持空单时，当日最低价低于观察买入价后，盘中价格反弹且超过反转买入价，采取 反转策略，即在该点位反手做多

        if marketPosition.marketPosition[self.symbol] > 0:
            if  last_price - marketPosition.averageEntryPrice[self.symbol] > last_price * STOP_PROFIT_PERCENT:
                trade_flag = 2
            if  marketPosition.averageEntryPrice[self.symbol] - last_price > last_price * STOP_LOSS_PERCENT:
                trade_flag = 2
        if marketPosition.marketPosition[self.symbol] < 0:
            if  last_price - marketPosition.averageEntryPrice[self.symbol] > last_price * STOP_LOSS_PERCENT:
                trade_flag = 2
            if  marketPosition.averageEntryPrice[self.symbol] - last_price > last_price * STOP_PROFIT_PERCENT:
                trade_flag = 2
        #止盈止损

        return  trade_flag
