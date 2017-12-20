from GlobalPramaters import *
from Global import *
import matplotlib.pyplot as plt

def get_trader(request_type):
    channel = grpc.insecure_channel('20.18.100.101:57500')
    stub = broker_pb2_grpc.BrokerStub(channel)
    response = stub.get_trader(broker_pb2.TraderRequest(trader_id=TRADER_ID,
                                                       trader_pin=TRADER_PIN,
                                                        request_type=request_type))
    return response

def new_order(request_type, order_id, side, symbol, volume, price, is_market, pos_type):
    channel = grpc.insecure_channel('20.18.100.101:57500')
    stub = broker_pb2_grpc.BrokerStub(channel)
    response = stub.new_order(broker_pb2.TraderRequest(trader_id=TRADER_ID,
                                                       trader_pin=TRADER_PIN,
                                                       request_type=request_type,
                                                       order_id=order_id,
                                                       side=side,
                                                       symbol=symbol,
                                                       volume=volume,
                                                       price=price,
                                                       is_market=is_market,
                                                       pos_type=pos_type))
    return  response


def record_performance(un_PNL):
    tmp = get_trader(common_pb2.FULL_INFO).positions
    positions = tmp.positions
    timestamp = tmp.timestamp

    tmp_PNL = {}
    for symbol in SYMBOLS:
        tmp_PNL[symbol] = 0

    if un_PNL is None:
        for symbol in SYMBOLS:
            un_PNL[symbol] = {'t':[],'value':[]}

    if hasattr(positions,'long_positions'):
        for symbol, value in enumerate(positions.long_positions):
            if hasattr(value,'realized_pnl'):
                tmp_PNL[symbol] = tmp_PNL[symbol] + value.realized_pnl
    if hasattr(positions,'short_positions'):
        for symbol, value in enumerate(positions.short_positions):
            if hasattr(value,'realized_pnl'):
                tmp_PNL[symbol] = tmp_PNL[symbol] + value.realized_pnl

    for symbol in SYMBOLS:
        un_PNL[symbol]['t'].append(timestamp)
        un_PNL[symbol]['value'].append(tmp_PNL[symbol])



def plotperformance(symbol, un_PNL):
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    plt.ion()
    plt.show()
    try:
        ax.lines.remove(lines[0])

    except Exception:
        pass

    lines = ax.plot(un_PNL[symbol]['t'], un_PNL[symbol]['value'] , "r-", lw=5)
    plt.pause(0.5)

# print(utils.get_trader(common_pb2.FULL_INFO))


def check_market_position(symbol):
    market_position = 0
    positions = get_trader(common_pb2.FULL_INFO).positions
    if hasattr(positions, 'long_positions') and positions.long_positions[symbol] is not None:
        if hasattr(positions.long_positions[symbol], 'volume'):
            if positions.long_positions[symbol].volume > 0:
                market_position = positions.long_positions[symbol].volume

    if hasattr(positions, 'short_positions') and positions.short_positions[symbol] is not None:
        if hasattr(positions.short_positions[symbol], 'volume'):
            if positions.short_positions[symbol].volume > 0:
                market_position = - positions.short_positions[symbol].volume
    return market_position


