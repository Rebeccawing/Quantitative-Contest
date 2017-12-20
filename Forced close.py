from GlobalPramaters import *
from Global import *

for symbol in SYMBOLS:
    order.insert_closePosition(symbol)
order.execute()

