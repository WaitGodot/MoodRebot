
from exchange.chbtc.chbtc_api_python import Client
from RebotConfig import RebotConfig
from Log import Log

import json
import time

PERIOD2TYPE = {
    1   :   '1min',
    3   :   '3min',
    5   :   '5min',
    15  :   '15min',
    30  :   '30min',
    60  :   '1hour',
    120 :   '2hour',
    240 :   '4hour',
    360 :   '6hour',
    720 :   '12hour',
}

STATUS = {
    0 : 'wait',
    1 : 'cannel',
    2 : 'compelete',
}

TYPE = {
    0 : 'sell',
    1 : 'buy',
}

def u2c(market):
    p = market.find('cny');
    return market[:p] + '_cny';

def c2u(market):
    p = market.find('_');
    return market[:p] + market[p+1:];

def PERIOD(period):
    return PERIOD2TYPE.get(period);

class chbtcEX():

    def set(self, access, sercet):
        self.client = Client(access_key='6b658f1b-8a44-41cc-b307-ae3e95cc7de1', secret_key='d19135ee-d071-4653-a1b9-5b8065a07efc');

    # function
    def getServerTimestamp(self):
        return self.client.time();

    def getUser(self):
        data = self.client.get('getAccountInfo');
        balance = data['result']['balance'];
        ret = [];
        for k,v in balance.items():
            ret.append({'currency':v['currency'].lower(), 'balance':v['amount']})
        return ret;

    def getMarkets(self):
        if  len(RebotConfig.rebot_trade_markets) > 0:
            return RebotConfig.rebot_trade_markets;
        return [];

    def getK(self, market, limit, period, timestamp=None):
        data = None;
        if timestamp==None:
            data = self.client.get('k', params={'currency': u2c(market), 'size':limit,'type':PERIOD(period)});
        else:
            data = self.client.get('k', params={'currency': u2c(market), 'size':limit,'type':PERIOD(period), 'since':timestamp});
        if data:
            return data['data'];
        return None;

    def getOrder(self, market):
        data = self.client.get('getOrdersIgnoreTradeType', {'currency':u2c(market), 'pageIndex':1, 'pageSize':100});
        code = 1000#data.get('code');
        if code and code != 1000:
            return None;
        for k, v in enumerate(data):
            v['side'] = TYPE[v['type']];
            v['market'] = c2u(v['currency']);
            v['volume'] = v['total_amount'];
            v['avg_price'] = v['trade_price'];
            v['remaining_volume'] = v['total_amount'] - v['trade_amount'];
            v['state'] = STATUS[v['status']];
        return data;

    def doOrder(self, market, side, price, volume, time=None, ext=None):
        cny = price * volume;
        if cny < 1:
            Log.d('\t\t market %s side %s price %f volume %f less 1' % (market, side, price, volume));
            return ;
        tradeType = 0;
        if side == 'buy':
            tradeType = 1;
        return self.client.get('order', params = {'price':price, 'amount':volume, 'tradeType':tradeType, 'currency':u2c(market)})

    def doOrderCancel(self, orderID, market):
        return self.client.get('cancelOrder', params ={'id':orderID, 'currency': u2c(market)});

class chbtcEXLocal():

    def set(self, access, sercet):
        self.client = Client(access_key='6b658f1b-8a44-41cc-b307-ae3e95cc7de1', secret_key='d19135ee-d071-4653-a1b9-5b8065a07efc');
        self.accounts = {
            'cny' : {'currency':'cny', 'balance':'%d' % RebotConfig.user_initamount, 'locked':'0.0'},
        };
        self.orders = {};
        self.marketOrders = {};
        self.ORDERID = 0;
        self.kss = {};
        self.poundage = 0.0001;

    def createOrder(self, market, side, time, price, volume, ext):
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
        currency = market[0:len(market)-3];

        o['remaining_volume']=0;
        o['executed_volume']=o['volume'];
        o['state']='done';

        if o['side'] == 'sell':
            c = self.accounts.get(currency);
            balance = float(c['balance']);
            c['balance'] = str(balance - o['executed_volume']);
            ccny = self.accounts.get('cny');
            ccny['balance'] = str(float(ccny['balance']) + o['executed_volume'] * o['avg_price'] * (1 - self.poundage) );
        if o['side'] == 'buy':
            c = self.accounts.get(currency);
            if c==None:
                self.accounts[currency] = {'currency':currency, 'balance':'0.0', 'locked':'0.0', 'price':0.0};
                c = self.accounts.get(currency);
            balance = float(c['balance']);
            price = c['price'];
            addbalance = o['executed_volume'] * (1 - self.poundage);
            addprice = o['avg_price'];

            c['balance'] = str(balance + addbalance);
            c['price'] = (balance)/(balance+addbalance)*price + addbalance/(balance+addbalance)*addprice;

            ccny = self.accounts.get('cny');
            ccny['balance'] = str(float(ccny['balance']) - addbalance*addprice);


    # function
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
        return [];
        #return [{'id':'anscny'},{'id':'btccny'}, {'id':'ethcny'}, {'id':'zeccny'}, {'id':'qtumcny'}, {'id':'gxscny'}, {'id':'eoscny'}, {'id':'sccny'}, {'id':'dgdcny'}, {'id':'1stcny'}, {'id':'btscny'}, {'id':'gntcny'}, {'id':'repcny'}, {'id':'etccny'}];
        #return [{'id':'anscny'}];

    def getK(self, market, limit, period, timestamp=None):
        if timestamp and timestamp < 1000000000000:
            timestamp *= 1000;

        if RebotConfig.rebot_is_test == False:
            data = None;
            if timestamp==None:
                data = self.client.get('k', params={'currency': u2c(market), 'size':limit,'type':PERIOD(period)});
            else:
                data = self.client.get('k', params={'currency': u2c(market), 'size':limit,'type':PERIOD(period), 'since':timestamp});
            if data:
                return data['data'];

        ks = self.kss.get(market);
        if ks==None:
            data = None;
            if timestamp==None:
                data = self.client.get('k', params={'currency': u2c(market), 'size':RebotConfig.rebot_test_k_count,'type':PERIOD(period)});
            else:
                data = self.client.get('k', params={'currency': u2c(market), 'size':RebotConfig.rebot_test_k_count,'type':PERIOD(period), 'since':timestamp});
            if data:
                self.kss[market] = data['data'];
                ks = self.kss.get(market);
                time.sleep(1);
        
        if ks == None:
            print '%s do not find kline' % market
        if timestamp > ks[-1][0]:
            print '{0} k line is over'.format(market);
            return None;
        ret = [];
        for k,v in enumerate(ks):
            if v[0] >= timestamp:
                ret.append(v);
            if len(ret) >= limit:
                return ret;
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
