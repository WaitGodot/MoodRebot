
from exchange.tushare.Client import Client
from RebotConfig import RebotConfig
from Log import Log

import json
import time
import math

PERIOD2TYPE = {
    1   :   '1',
    3   :   '3',
    5   :   '5',
    15  :   '15',
    30  :   '30',
    60  :   '60',
    240 :   'd',
    1680:   'w',
}

def TIMEINTERVAL(lastt, period, count):
    if period == 240:
        return lastt + count * 24 * 60 * 60;
    if period == 1680:
        return lastt + count * 7 * 24 * 60 * 60;
    return lastt + count * period * 60;
def PERIOD(period):
    return PERIOD2TYPE.get(period);
def TIMESTAMP(period, timestamp):
    st=None;
    if period >= 240:
        st = time.strftime("%Y-%m-%d", time.localtime(timestamp));
    else:
        st = time.strftime("%Y-%m-%d %H:%M", time.localtime(timestamp));
    return st;
class tushareEX():

    def set(self, access, sercet):
        self.client = Client();
    # function
    def loadData(self, period, timestamp):
        self.client.loadData(PERIOD(period), TIMESTAMP(period, timestamp));

    def prepare(self, period, timestamp):
        self.client.prepare(PERIOD(period), TIMESTAMP(period, timestamp));

    def getServerTimestamp(self):
        return self.client.time();

    def getUser(self):
        return None;

    def getMarkets(self):
        if  len(RebotConfig.rebot_trade_markets) > 0:
            return RebotConfig.rebot_trade_markets;
        return [];

    def getK(self, market, limit, period, timestamp=None):
        st=None;
        if timestamp != None:
            if period >= 240:
                st = time.strftime("%Y-%m-%d", time.localtime(timestamp));
            else:
                st = time.strftime("%Y-%m-%d %H:%M", time.localtime(timestamp));
        data = self.client.getK(market, PERIOD(period), st);
        for k,v in enumerate(data):
            if period >= 240:
                v[0] = time.mktime(time.strptime(v[0], "%Y-%m-%d"));
            else:
                v[0] = time.mktime(time.strptime(v[0], "%Y-%m-%d %H:%M"));
        return data;

    def getOrder(self, market):
        return None;

    def doOrder(self, market, side, price, volume, time=None, ext=None):
        return None;

    def doOrderCancel(self, orderID, market):
        return None;


class tushareEXLocal():

    def set(self, access, sercet):
        self.client = Client();
        self.accounts = {
            'cny' : {'currency':'cny', 'balance':'%d' % RebotConfig.user_initamount, 'locked':'0.0'},
        };
        self.orders = {};
        self.marketOrders = {};
        self.ORDERID = 0;
        self.kss = {};
        self.allMarkets = None;
        self.currentMarkets = None;
        self.poundage = 0;#0.0001;

    def loadData(self, period, timestamp):
        self.client.loadData(PERIOD(period), TIMESTAMP(period, timestamp));

    def prepare(self, period, timestamp):
        self.client.prepare(PERIOD(period), TIMESTAMP(period, timestamp));

    def refresh(self, period, market):
        self.client.refresh(PERIOD(period), market);

    def createOrder(self, market, side, time, price, volume, ext):
        volume = math.floor(volume/100)*100;
        if volume<=0:
            return None;
        self.ORDERID += 1;
        id = self.ORDERID;
        o = {
            'id':id,
            'side':side, # sell, buy
            'price':price,
            'avg_price':price,
            'state':'wait', # wait, done, cancel
            'market':market,
            'created_at':time,
            'volume':volume,
            'remaining_volume':volume,
            'executed_volume':0,
            'ext':ext
        }
        self.orders[id] = o;
        d = self.marketOrders.get(market);
        if d==None:
            self.marketOrders[market] = [];
            d = self.marketOrders.get(market);
        d.append(o);
        return id;

    def compeleteOrder(self, id):
        o = self.orders.get(id);
        if o==None:
            return;
        market = o['market'];
        currency = market;#market[0:len(market)-3];

        o['remaining_volume']=0;
        o['executed_volume']=o['volume'];
        o['state']='done';

        if o['side'] == 'sell':
            c = self.accounts.get(currency);
            balance = float(c['balance']);
            c['balance'] = str(balance - o['executed_volume']);
            ccny = self.accounts.get('cny');
            ccny['balance'] = str(float(ccny['balance']) + o['executed_volume'] * o['avg_price'] * (1 - self.poundage) );
            print '\t\tsell', market, balance, c['balance']
        if o['side'] == 'buy':
            c = self.accounts.get(currency);
            if c==None:
                self.accounts[currency] = {'currency':currency, 'balance':'0.0', 'locked':'0.0', 'price':0.0};
                c = self.accounts.get(currency);
            balance = float(c['balance']);
            price = c['price'];
            addbalance = o['executed_volume'] * (1 - self.poundage);
            addprice = o['avg_price'];

            print '\t\tbuy',market, balance, addbalance
            c['balance'] = str(balance + addbalance);
            c['price'] = (balance)/(balance+addbalance)*price + addbalance/(balance+addbalance)*addprice;

            ccny = self.accounts.get('cny');
            ccny['balance'] = str(float(ccny['balance']) - addbalance*addprice);


    # function
    def getNextKTime(self, period, timestamp):
        return TIMEINTERVAL(timestamp, period, 1);

    def getServerTimestamp(self):
        return self.client.time();

    def getUser(self):
        d = {}
        accounts = [];
        for k,v in self.accounts.items():
            accounts.append(v);
        d['accounts']=accounts;
        return d;

    def getMarkets(self):
        if  len(RebotConfig.rebot_trade_markets) > 0:
            return RebotConfig.rebot_trade_markets;

        return self.client.getMarkets();
        #return [{'id':'anscny'},{'id':'btccny'}, {'id':'ethcny'}, {'id':'zeccny'}, {'id':'qtumcny'}, {'id':'gxscny'}, {'id':'eoscny'}, {'id':'sccny'}, {'id':'dgdcny'}, {'id':'1stcny'}, {'id':'btscny'}, {'id':'gntcny'}, {'id':'repcny'}, {'id':'etccny'}];
        #return [{'id':'anscny'}];

    def getK(self, market, limit, period, timestamp=None):
        ret = [];
        ks = self.kss.get(market);
        timestamp = time.mktime(time.strptime(time.strftime('%Y-%m-%d', time.localtime(timestamp)), "%Y-%m-%d"));
        if ks==None:
            data = self.client.getK(market, PERIOD(period), TIMESTAMP(period, timestamp));
            if data is not None:
                ndata = data.values.tolist();
                for k,v in enumerate(ndata):
                    if period >= 240:
                        v[0] = time.mktime(time.strptime(str(v[0]), "%Y-%m-%d"));
                    else:
                        v[0] = time.mktime(time.strptime(v[0], "%Y-%m-%d %H:%M"));
                    
                # print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ndata[-1][0])), data.values[-1][0];
                self.kss[market] = ndata;
                ks = self.kss.get(market);

        if ks == None or len(ks) == 0:
            # print '%s do not find kline' % market
            return ret;
        if timestamp > ks[-1][0]:
            # print '{0} k line is over'.format(market);
            return ret;
        pp = TIMEINTERVAL(timestamp, period, limit);
        # print market, len(ks), time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp)), time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(pp)), time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ks[-1][0]));
        for k,v in enumerate(ks):
            # print timestamp, v[0], pp, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(v[0]))
            if v[0] >= timestamp and v[0] < pp:
                ret.append(v);
            if len(ret) >= limit:
                return ret;
        # print ret;
        return ret;

    def getOrder(self, market):
        ret = self.marketOrders.get(market);
        if ret==None:
            return [];
        return ret;

    def doOrder(self, market, side, price, volume, time=None, ext=None):
        id = self.createOrder(market, side, time, price, volume, ext)
        if id:
            self.compeleteOrder(id);

    def doOrderCancel(self, orderID):
        return None;
