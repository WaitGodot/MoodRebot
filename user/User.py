# user
#
#
from user.Order import Order
from RebotConfig import RebotConfig
import math

class User():
    instanse = None;
    def Instanse():
        if User.instanse == None:
        	user.instanse = User();
        return user.instanse;

    def __init__(self):
        self.amount = 0; # cash
        self.initamount = RebotConfig.user_initamount;
        self.positions = {}; # [market]=count
        self.orders = {};
        self.tradetimes = 0;
        self.wintimes = 0;

    def setHigh(self, market, high):
        pc = self.positions.get(market);
        if pc:
            pc['high'] = high;

    def getAllCost(self):
        s = 0
        for key, value in(self.positions.items()):
            s += value['volume'] * value['price'];
        return s;

    def getCost(self, currency):
        pc = self.positions.get(currency);
        if pc==None:
            return None;
        return pc['volume'] * pc['price'];

    def getHighCost(self, currency):
        pc = self.positions.get(currency);
        if pc==None:
            return None;
        return pc['volume'] * pc['high'];

    def getOrderMarket(self, market):
        d = [];
        for k,v in(self.orders.items()):
            if v.market == market:
                d.append(v);
        return d;
    def updateCost(self, currency, cost):
        pc = self.positions.get(currency);
        if pc:
            pc['price'] = cost;
    def updateHigh(self, currency, hp):
        pc = self.positions.get(currency);
        if pc:
            if hp > pc['high']:
                pc['high'] = hp;

    def updatePositions(self, positions):
        for key, value in enumerate(positions):
            vol = float(value['balance']);# - float(value['locked']);
            price = value.get('price');
            currency = value['currency'];
            pc = self.positions.get(currency);
            if pc==None:
                self.positions[currency] = {'volume':0, 'price':1, 'high':0}; # default.
                pc = self.positions[currency];
            if price!=None:
                pc['price'] = price;
            pc['volume']=vol;
            if currency==RebotConfig.base_currency:
                self.amount = vol;

    def updateOrder(self, orders):
        norders = [];
        for key, value in enumerate(orders):
            id   = value['id'];
            type = value['side'];
            market = value['market'];
            t = value['created_at'];
            price = value['price'];
            volume = value['volume'];
            averageprice = value['avg_price'];
            leftvolume = value['remaining_volume'];
            state = value['state'];
            ext = value.get('ext');

            o = self.orders.get(id);
            if o:
                if state == 'cancel':
                    o.update(averageprice, leftvolume, 'cancel');
                else:
                    o.update(averageprice, leftvolume);
            else:
                if state != 'cancel' and state != 'compelete':
                    o = Order(id, type, market, t, price, volume, ext);
                    self.orders[id] = o;
                    self.setHigh(market[0:len(market)-len(RebotConfig.base_currency)], 0);
            if o:
                if o.status == "uncompelete":
                    norders.append(o);
                else:
                    del self.orders[id];
        return norders;

    def doOrder(self, market, side, price, volume=None):
        if side == 'buy':
            if volume==None:
                if self.amount < RebotConfig.user_asset_least:
                    volume = self.amount / price;
                else:
                    cleastamount = self.amount/RebotConfig.user_asset_ratio 
                    if cleastamount < RebotConfig.user_asset_least:
                        cleastamount = RebotConfig.user_asset_least;
                    volume = cleastamount / price ;
            # volume = math.floor(volume/100)*100;
            amount = price * volume;
            if amount > self.amount:
                amount = self.amount;
                volume = amount / price;
                # volume = math.floor(volume/100)*100;
            if volume < RebotConfig.user_least_vol:
                return 0;
            if self.amount < 6:
                return 0;
            self.amount = self.amount - amount;
            return volume;
        if side == 'sell':
            currency = market[0:len(market) - len(RebotConfig.base_currency)];
            pc = self.positions.get(currency);
            if pc==None:
                return;
            v = pc['volume'];
            if pc == None or v <= 0:
                print "\t\tnot enough positions, market : {0}".format(currency);
                return 0;
            if volume==None:
                volume = v;
            if v < volume:
                volume = v;
            return volume;

