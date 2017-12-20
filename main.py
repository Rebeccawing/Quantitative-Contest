from GlobalPramaters import *
from Global import *
import Data_processing
import utils
import csv
import R_Breaker

un_PNL = None

#print(new_order(common_pb2.NEW_ORDER,2,common_pb2.BID,"A001.PSE",1,0,True,common_pb2.LONG))
#print(new_order(common_pb2.NEW_ORDER,2,common_pb2.ASK,"A001.PSE",1,123,False,common_pb2.LONG))


if __name__ == '__main__':
    channel = grpc.insecure_channel('20.18.100.101:57600')  # 57500
    stub = market_data_pb2_grpc.MarketDataStub(channel)
    response = stub.subscribe(common_pb2.Empty())
    strategies = {}
    strategy1s = {}
    strategy2s = {}
    strategy3s = {}
    pre_orders = {}
    modes = {}
    last_price = {}
    for symbol in SYMBOLS:
        strategies[symbol] = Data_processing.Strategies()
        strategy1s[symbol] = Data_processing.DualThrust()
        #strategy1s[symbol] = R_Breaker.R_Breaker(symbol=symbol,Run_freq=20,data_freq=60)
        #strategy2s[symbol] = Data_processing.GFTD(symbol=symbol,Run_freq=20,data_freq=15)
        #strategy3s[symbol] = Data_processing.DualThrust()
    # strategy2s[symbol] = Data_processing.GFTD(symbol=symbol,Run_freq=20,data_freq=15)
    strategy2s[SYMBOLS[0]] = Data_processing.GFTD(Run_freq=30, data_freq=30,n1=2,n2=3,n3=5)
    strategy2s[SYMBOLS[1]] = Data_processing.GFTD(Run_freq=30, data_freq=30,n1=2,n2=5,n3=2)
    strategy2s[SYMBOLS[2]] = Data_processing.GFTD(Run_freq=30, data_freq=30,n1=2,n2=6,n3=4)
    strategy2s[SYMBOLS[3]] = Data_processing.GFTD(Run_freq=30, data_freq=30, n1=4, n2=4, n3=4)
    strategy2s[SYMBOLS[4]] = Data_processing.GFTD(Run_freq=30, data_freq=30, n1=3, n2=2, n3=4)
    strategy2s[SYMBOLS[5]] = Data_processing.GFTD(Run_freq=30, data_freq=30, n1=3, n2=4, n3=4)
    modes[SYMBOLS[0]] = Data_processing.mode(rmean=0.0203994492797)
    modes[SYMBOLS[1]] = Data_processing.mode(rmean=0.164587904643)
    modes[SYMBOLS[2]] = Data_processing.mode(rmean=0.118585113226)
    modes[SYMBOLS[3]] = Data_processing.mode(rmean=0.0203994492797)
    modes[SYMBOLS[4]] = Data_processing.mode(rmean=0.164587904643)
    modes[SYMBOLS[5]] = Data_processing.mode(rmean=0.118585113226)



    counter = 0


    for market_data in response:
        #print(market_data)
        instruments = market_data.instruments

        for instrument in instruments:
            if instrument.symbol in SYMBOLS:
                #print(instrument.symbol)
                last_price[instrument.symbol] = instrument.last_price
                counter = counter + 1
                ## 调用策略对象
                #print(instrument.last_price)
                #print(strategies[instrument.symbol])
                FacName = instrument.symbol
                with open("C:\DELL\internship\wequant\TradingSystem-10\TradingSystem-10\data\\"+FacName+".csv",'a') as fp:
                    a = csv.writer(fp);
                    price = [instrument.last_price]
                    a.writerow(price)

                strategies[instrument.symbol].add_Market_data(instrument.last_price)
                strategy1s[instrument.symbol].add_Market_data(instrument.last_price)
                strategy2s[instrument.symbol].add_Market_data(instrument.last_price)
                #strategy3s[instrument.symbol].add_Market_data(instrument.last_price)
                modes[instrument.symbol].add_Market_data(instrument.last_price)
                modes[instrument.symbol].judge()
                print('modes: %s'%(modes[instrument.symbol].flag))
                pre_orders[instrument.symbol] = strategies[instrument.symbol].run_timely(Marketjudge=modes[instrument.symbol].flag,strategy1=strategy1s[instrument.symbol],strategy2=strategy2s[instrument.symbol])
                #pre_orders[instrument.symbol] = strategies[instrument.symbol].run_timely(False,strategy1=strategy1s[instrument.symbol],strategy2=strategy2s[instrument.symbol])


            trade_shares = int(TOTAL_TRADE_SHARES/len(SYMBOLS))
            print(pre_orders)


            for symbol in pre_orders.keys():
                if pre_orders[symbol] == 1:
                    if marketPosition.marketPosition[symbol] == 0:
                        order.insert_openLongPosition(symbol=symbol, volume=trade_shares, price=None, is_market= True)
                    if marketPosition.marketPosition[symbol] <= -1:
                        order.insert_closePosition(symbol=symbol)
                        order.insert_openLongPosition(symbol=symbol, volume=trade_shares, price=None, is_market=True)
                if pre_orders[symbol] == -1:
                    if marketPosition.marketPosition[symbol] == 0:
                        order.insert_openShortPosition(symbol=symbol, volume=trade_shares, price=None, is_market=True)
                    if  marketPosition.marketPosition[symbol] >= 1:
                        order.insert_closePosition(symbol=symbol)
                        order.insert_openShortPosition(symbol=symbol, volume=trade_shares, price=None, is_market=True)
                if pre_orders[symbol] == 2: #平仓
                    order.insert_closePosition(symbol)

            #----------------------------------------------
            order.execute()
            # ----------------------------------------------


            if counter >= 10:
                counter = 0
                # 全局止盈止损
                for symbol in SYMBOLS:
                    isNeedClose = False
                    if marketPosition.marketPosition[symbol] > 0:
                        if last_price[symbol] - marketPosition.averageEntryPrice[symbol] > last_price[symbol] * STOP_PROFIT_PERCENT:
                            isNeedClose = True
                        if marketPosition.averageEntryPrice[symbol] - last_price[symbol] > last_price[symbol] * STOP_LOSS_PERCENT:
                            isNeedClose = True
                    if marketPosition.marketPosition[symbol] < 0:
                        if last_price[symbol] - marketPosition.averageEntryPrice[symbol] > last_price[symbol] * STOP_LOSS_PERCENT:
                            isNeedClose = True
                        if marketPosition.averageEntryPrice[symbol] - last_price[symbol] > last_price[symbol] * STOP_PROFIT_PERCENT:
                            isNeedClose = True
                    if isNeedClose:
                        order.insert_closePosition(symbol)
                ## 更新仓位
                marketPosition.renew_all_market_position()






            ## 测试订单系统
            """
            OrderBuf.insert_openLongPosition(SYMBOLS[0], 2 ,None, True)
            OrderBuf.insert_openShortPosition(SYMBOLS[1],2,None,True)
            OrderBuf.execute()
            print('insert')
            print(marketPosition.renew_all_market_position())

            for symbol in SYMBOLS:
                OrderBuf.insert_closePosition(symbol)
            OrderBuf.execute()
            print('delete')
            print(marketPosition.renew_all_market_position())
            """

