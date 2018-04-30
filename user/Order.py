
import time
from RebotConfig import RebotConfig

# order
# 
# order type
# sell, buy
# order status
# compelete, uncompelete, cancel

class Order():
    ORDERID = 0;
    def __init__(self, id, type, market, time, price, volume, ext):
        Order.ORDERID += 1;
        self.orderid = Order.ORDERID;
        self.parent = Order.ORDERID;
        self.id = id;
        self.type = type;
        self.market = market;
        self.time = time;
        self.userprice = price;
        self.averageprice = 0;
        self.volume = volume;
        self.leftvolume = volume;
        self.status = "uncompelete"
        self.ext = ext;
    
    def update(self, averageprice, leftvolume, status=None):
        self.averageprice = averageprice;
        self.leftvolume = leftvolume;
        if self.leftvolume <= 0:
            self.status = "compelete";
        if status != None:
            self.status = status;

    def checkMustCancel(self):
        if RebotConfig.rebot_is_test:
            return False;
        return time.time() - self.time > RebotConfig.rebot_period * 60/5 and self.status != "compelete";

    def __str__(self):
        return "orderid:{0}, id:{1}, type:{2}, market:{3}, time:{4}, user price:{5}, average price:{6}, volume:{7}, left volume:{8}, status:{9}, ext:{10}".format(self.orderid, self.id, self.type, self.market, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.time)), self.userprice, self.averageprice, self.volume, self.leftvolume, self.status, self.ext);
