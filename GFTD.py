from GlobalPramaters import *
from Global import *

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import xlrd
import sys
import os
import Data_processing

class GFTD(Data_processing.Strategies):
    price = 0
    gap = 0
    Run_freq = 15
    data_freq = 0.2
    n1 =4
    n2 = 4
    n3 = 4

    def __init__(self,data_freq,Run_freq, n1, n2, n3,gap=0.2):
        super(GFTD, self).__init__()
        self.data_freq = data_freq
        self.gap = gap
        self.Run_freq = Run_freq
        self.n1 = n1
        self.n2 = n2
        self.n3 = n3

    def run(self):
        self.clo = self.PriceList[0::self.data_freq*int(1/self.gap)]
        self.high = [max(self.PriceList[int((i)/self.gap):int((i+1)/self.gap)] for i in range(0,len(self.FreqList(data_freq))))]
        self.low = [min(self.PriceList[int((i)/self.gap):int((i+1)/self.gap)] for i in range(0,len(self.FreqList(data_freq))))]
        self.trade = 0
        self.ud = np.zeros((len(self.clo),), dtype=np.int32)
        for i in range(n1,len(self.clo)):
            if self.clo[i]>self.clo[i-self.n1]:
                self.ud[i] = 1
            elif self.clo[i]<self.clo[i-self.n1]:
                self.ud[i] = -1
            else:
                pass


        self.ud_sum = self.ud.copy()
        for i in range(self.n1,len(self.ud)):
            if self.ud[i] == self.ud[i-1]:
                self.ud_sum[i] = self.ud_sum[i-1] + self.ud[i]
            else:
                self.ud_sum[i] = self.ud[i]
        self.buy_start = np.zeros((len(self.clo),), dtype=np.int32)
        self.sell_start = np.zeros((len(self.clo),), dtype=np.int32)
        k1 = k2 = 0
        for i in range(self.n1,len(self.clo)):
            if self.ud_sum[i] == -self.n2:
                self.buy_start[k1] = i
                k1 = k1 + 1
            elif self.ud_sum[-1] == self.n2:
                self.sell_start[k2] = i
                k2 = k2 + 1
            else:
                pass
        self.buy_start = [self.buy_start[i] for i in range(0,len(self.buy_start)) if not self.buy_start[i] ==0 ]
        self.sell_start = [self.buy_start[i] for i in range(0,len(self.sell_start)) if not self.sell_start[i] == 0 ]
        last_buy = self.buy_start[-1]
        t_buy = len(self.clo) - last_buy
        self.buy_count = 0
        if t_buy >2:
            for i in range(2,t_buy):
                if ((self.clo[last_buy + i] >= self.high[last_buy + i - 2]) and (self.high[last_buy + i] > self.high[last_buy + i - 1]) and (
                            self.clo[last_buy + i] > self.clo[last_buy+1])):
                    self.buy_count = self.buy_count + 1
                if self.buy_count == self.n3:
                    self.trade = 1
                    break
        last_sell = self.sell_start[-1]
        t_sell = len(self.clo) - last_sell
        self.sell_count = 0
        if t_sell>2:
            for i in range(2,t_sell):
                if (self.clo[last_sell + i] <= self.low[last_sell + i - 2]) and (self.low[last_sell + i] < self.low[last_sell + i - 1]) and (
                            self.clo[last_sell + i] < self.clo[last_sell+1]):
                    self.sell_count = self.sell_count + 1
                if self.sell_count == self.n3:
                    self.trade = -1
                    break


        last = len(self.clo)
        if last_buy>last_sell:
            self.stop_loss = min(self.low[last_buy:last])
            if self.clo[-1] <= self.stop_loss:
                self.trade = 2
        else:
            self.stop_loss = min(self.high[last_sell:last])
            if self.clo[-1] >= self.stop_loss:
                self.trade = 2

        return self.trade
