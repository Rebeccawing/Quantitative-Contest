
import pandas as pd
import pdb
import numpy as np
import math
from PyEMD import EMD
import pdb


class Strategies(object):
    def __init__(self,gap=0.1):
        self.PriceList =[]
        self.gap = gap


    def FreqList(self,freq=15):
        return self.PriceList[0::int(freq*int(1/self.gap))]

    def add_Market_data(self, price,symbol=0):
        self.PriceList.append(price)
        return self.PriceList.append(price)


    def run_timelybacktest(self,strategy):
        if len(self.PriceList)%int(strategy.Run_freq/self.gap) ==0 and len(self.PriceList)>0:
            return strategy.run()
        else:
            return 0


################################################################################################################################################3
    def run_timely(self, Marketjudge, strategy1, strategy2):
        #if self.Market_Judge:  # 趋势情况
        if Marketjudge:
            strategy = strategy1

        else:  # 震荡情况
            strategy = strategy2

        if len(self.PriceList) % int(strategy.Run_freq / strategy.gap) == 0 and len(
            self.PriceList) > 0:  # freq 和 Runfreq 单位是秒
            return strategy.run()
        else:
            return 0
###############################################################################################################################################3333




    def Peformance(self, strategy,account,shares):


        if  self.run_timelybacktest(strategy) is not 0:
            #pdb.set_trace()

            shares.append(account[-1]*self.run_timelybacktest(strategy)/self.PriceList[-1])


            account.append(shares[-1]*self.PriceList[-1] + account[-1]*(1-self.run_timelybacktest(strategy)))


        else:


            account.append(shares[-1]*(self.PriceList[-1]-self.PriceList[-2]) + account[-1])


        return account, shares



class mode(Strategies):

    def __init__(self,data_freq=15,Run_freq=90,gap=0.1,rmean = 0.1):
        super(mode, self).__init__()
        self.data_freq = data_freq
        self.Run_freq = Run_freq
        self.gap = gap
        self.rmean = rmean
        self.flag = True

#取时间窗口算收盘价序列的震荡情况，倾向于取1分钟，即
    def imff(self):
        temp = self.data_freq*int(1/self.gap)
        self.price = self.PriceList[-int(self.data_freq/self.gap):-1]
        s = np.array(self.price)
        emd = EMD()
        IMFs = emd.emd(s)
        r = IMFs[-1]
        a = np.std(r)
        b = np.std(s-r)
        self.r = math.log(b/a)

    def judge(self):
        ##1是趋势，0是震荡          1用R-B，0用GFTD
        if len(self.PriceList)%int(self.Run_freq/self.gap) ==0 and len(self.PriceList)>0:
            self.imff()
            if self.r <= self.rmean:
                self.flag = True
            elif self.r > self.rmean:
                self.flag = False
        return self.flag





class DualThrust(Strategies):
    '''
     其中K1,K2我参数
     N_min为策略的执行频率
     data_freq则是获取的windows
    '''
     # gap现在是0.2秒的时间即那个，明天应该是0.1

    def __init__(self, k1=0.03,k2=0.02,Run_freq =10,freq=2):
        super(DualThrust, self).__init__()
        self.K1 =k1
        self.K2= k2
        self.Run_freq = Run_freq
        self.data_freq =freq



    @property
    def Open(self):
        return self.PriceList[-int(self.data_freq/self.gap)]


    @property
    def HC(self):

        return max(self.FreqList(freq=self.data_freq)[-self.Run_freq-1:-1])
    @property
    def LL(self):
        #pdb.set_trace()
        return min([min(self.PriceList[-int((i + 1) / self.gap) - 1:-int(i / self.gap)-1]) for i in range(self.Run_freq)])
    @property
    def HH(self):
        return max([max(self.PriceList[-int((i+1)/self.gap)-1:-int(i/self.gap)-1]) for i in range(self.Run_freq)])
    @property
    def LC(self):
        return min(self.FreqList(freq=self.data_freq)[-self.Run_freq-1:-1])

    @property
    def Range(self):

        return max(self.HC-self.LL,self.HH-self.LC)

    @property
    def Sellline(self):
        return self.Open-self.Range*self.K1

    @property
    def Buyline(self):
        return self.Open +self.Range*self.K2



    def run(self):

        if self.PriceList[-1] > self.Buyline:
            return 1
        elif self.PriceList[-1] < self.Sellline:
            return -1
        else:
            return 0

class GFTD(Strategies):

    def __init__(self,data_freq=30,Run_freq=30, n1=4, n2=4, n3=4,gap=0.1):
        super(GFTD, self).__init__()
        self.data_freq = data_freq
        self.gap = gap
        self.Run_freq = Run_freq
        self.n1 = n1
        self.n2 = n2
        self.n3 = n3

    @property
    def high(self):

       # pdb.set_trace()
        z =int(self.data_freq/self.gap)

        return  [max(self.PriceList[i*z:(i+1)*z]) for i in range(0,len(self.FreqList(freq=self.data_freq)))]

    @property
    def low(self):
        z = int(self.data_freq / self.gap)
        return [min(self.PriceList[i*z:(i+1)*z]) for i in range(0,len(self.FreqList(freq=self.data_freq)))]

    def run(self):
        #pdb.set_trace()

        self.clo = self.PriceList[0::int(self.data_freq*int(1/self.gap))]
        self.trade = 0
        self.ud = np.zeros((len(self.clo),), dtype=np.int32)
        for i in range(self.n1,len(self.clo)):
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
            elif self.ud_sum[i] == self.n2:
                self.sell_start[k2] = i
                k2 = k2 + 1
            else:
                pass
        self.buy_start = [self.buy_start[i] for i in range(0,len(self.buy_start)) if not self.buy_start[i] ==0 ]
        self.sell_start = [self.sell_start[i] for i in range(0,len(self.sell_start)) if not self.sell_start[i] == 0 ]
        last_buy = 0
        last_sell = 0
        if len(self.buy_start):
            last_buy = self.buy_start[-1]
            t_buy = len(self.clo) - last_buy - 1
            self.buy_count = 0
        #pdb.set_trace()
            if t_buy >2:
                for i in range(2,t_buy):
                    if ((self.clo[last_buy + i] >= self.high[last_buy + i - 2]) and (self.high[last_buy + i] > self.high[last_buy + i - 1]) and (self.clo[last_buy + i] > self.clo[last_buy+1])):
                        self.buy_count = self.buy_count + 1
                    if self.buy_count == self.n3:
                        self.trade = 1
                        break

        if len(self.sell_start):
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
        # pdb.set_trace()
        #if last_buy>last_sell:
        #    self.stop_loss = min(self.low[last_buy:last])
        #    if self.clo[-1] <= self.stop_loss:
        #        self.trade = 2
        #else:
        #    self.stop_loss = min(self.high[last_sell:last])
        #    if self.clo[-1] >= self.stop_loss:
        #        self.trade = 2

        return self.trade



if __name__ == "__main__":

    Data1 =pd.read_csv("C:\DELL\internship\wequant\\A002.PSE.csv").iloc[:,1]


    # 创建一个策略
    GFTD1 =GFTD(0.2,15,4,4,4,0.2)
    account=[]
    shares =[]

    for price in Data1:
        #print(price)

        GFTD1.add_Market_data(price=price)

        if len(GFTD1.PriceList) ==1:
            account.append(10000)
            shares.append(0)

        else:
            account,shares =GFTD1.Peformance(GFTD1,account,shares)
    print(account)
