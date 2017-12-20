import pandas as pd
import numpy as np
import datetime as dt
from datetime import timedelta
from PyEMD import EMD
import math
import Data_processing

class mode(Data_processing.Strategies):
    price = 0
    data_freq = 0
    Run_freq = 0
    gap = 0.2

    def __init__(self,price,data_freq,Run_freq,gap):
        self.price = price
        self.data_freq = data_freq
        self.Run_freq = Run_freq
        self.gap = gap

#取时间窗口算收盘价序列的震荡情况，倾向于取1分钟，即
    def IMFs(self,win):
        temp = self.data_freq*int(1/self.gap)
        self.price = self.PriceList[-60/int(self.gap):-1]
        s = self.price
        emd = EMD()
        IMFs = emd.emd(s)
        r = IMFs[-1]
        b = np.std(s-r)
        self.r = math.log(b/a)

    def judge(self,rmean):
        ##1是趋势，0是震荡          1用R-B，0用GFTD
        if self.r <= rmean:
            super(self).Market_Judge = 1
        elif self.r > rmean:
            super(self).Market_Judge = 0
        return self.Market_Judge

