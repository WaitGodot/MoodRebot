from RebotConfig import RebotConfig
from Log import Log
from exchange.huobi.HuobiUtil import *
from exchange.huobi.HuobiService import *
import json
import time
import math

'''{1min, 5min, 15min, 30min, 60min, 1day, 1mon, 1week, 1year }'''
PERIOD2TYPE = {
    1   :   '1min',
    5   :   '5min',
    15  :   '15min',
    30  :   '30min',
    60  :   '60min',
}

def PERIOD(period):
    if period >= 60:
        return '60min';
    return PERIOD2TYPE.get(period);

def TIMEHOUR(timestamp):
    return float(time.strftime("%H", time.localtime(timestamp)));

def CreateDefalutKline():
    return {
        'id'    : 0,
        'open'  : 0,
        'high'  : 0,
        'low'   : 999999999,
        'close' : 0,
        'vol'   : 0, }

def SortCompare(a, b):
    return a['id'] < b['id'];
def Cut(num, c):
    s = '{:.9f}'.format(num);
    pos = s.find('.');
    if pos > 0:
        return float(s[0:pos+c+1]);
    else:
        return num;
def ConvertData(preiod1, data, period2):
    ndata = [];
    kcount = period2 / preiod1;
    datalenght = len(data);
    nk = None;

    for key in range(1, datalenght):
        k = data[datalenght - 1 - key];
        prek = data[datalenght - key];

        h = TIMEHOUR(k['id']);
        idx = h % kcount;

        if idx == 0:
            if nk != None:
                nk['close'] = prek['close'];
                nk['high']  = max(nk['high'], prek['high']);
                nk['low']   = min(nk['low'], prek['low']);
                nk['vol']   = nk['vol'] + nk['prevol'];

            nk = CreateDefalutKline();
            ndata.append(nk);
            nk['id']    = k['id'];
            nk['open']  = k['open'];
            nk['prevol'] = 0;
            nk['idx'] = idx;

        if nk != None:
            nk['close'] = k['close'];
            nk['high']  = max(nk['high'], k['high']);
            nk['low']   = min(nk['low'], k['low']);
            if nk['idx'] != idx:
                nk['prevol'] += prek['vol'];
                nk['idx'] = idx;
            nk['vol'] = nk['prevol'] + k['vol'];

    ndata.reverse();
    #for k,v in enumerate(ndata):
    #    print v, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(v['id']));
    return ndata;

def ConvertKlineData(data):
    ndata = [];
    lendatadata = len(data);
    for k in range(0, lendatadata):
        v = data[lendatadata - 1 - k];
        d = [0,1,2,3,4,5];
        d[0] = v['id'];
        d[1] = v['open'];
        d[2] = v['high'];
        d[3] = v['low'];
        d[4] = v['close'];
        d[5] = v['vol'];
        ndata.append(d);
    return ndata;

class huobiEX():

    def set(self, access, secret):
        set_user_key(access, secret);
        self.orders = {};
        self.marketOrders = {};
        self.precisions = {};
    def createOrder(self, id, market, side, time, price, volume, ext):
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
            'ext':ext,
        }
        self.orders[id] = o;
        d = self.marketOrders.get(market);
        if d==None:
            self.marketOrders[market] = [];
            d = self.marketOrders.get(market);
        d.append(o);
        return id;
    def getPrice(self, market, price):
        d = self.precisions[market];
        if d != None:
            return round(price, int(d['price-precision']));
        else :
            return round(price, 0);
    def getVolume(self, market, vol):
        d = self.precisions[market];
        if d != None:
            return Cut(vol, int(d['amount-precision']));
        else :
            return Cut(vol, 0);
    # function
    def loadData(self, period, timestamp):
        return None;

    def prepare(self, period, timestamp):
        d = get_symbols();
        for k,v in enumerate(d['data']):
            if v['quote-currency'] == 'usdt':
                key = v['base-currency'] + 'usdt';
                self.precisions[key] = v;

    def getServerTimestamp(self):
        return time.time();

    def getUser(self):
        data = get_balance();
        nndata = [];
        if data['status'] != 'ok':
            return {'accounts':nndata};
        if data['data']['state'] != 'working':
            return {'accounts':nndata};
        listdata = data['data']['list'];
        ndata = {};
        for k,v in enumerate(listdata):
            currency = v['currency'];
            c = ndata.get(currency);
            if c == None:
                c = {'currency': currency};
                ndata[currency] = c;
            if v['type'] == 'trade':
                c['balance'] = float(v['balance']);
            if v['type'] == 'frozen':
                c['locked'] = float(v['balance']);
        for k,v in enumerate(ndata):
            d = ndata.get(v);
            if d['balance'] > 0 or d['locked'] > 0:
                nndata.append(d);
        return {'accounts':nndata};

    def getMarkets(self):
        if  len(RebotConfig.rebot_trade_markets) > 0:
            return RebotConfig.rebot_trade_markets;
        return [];

    def getK(self, market, limit, period, timestamp=None):
        data = None;
        if period > 60:
            data = get_kline(market, PERIOD(period), limit * period / 60);
        else:
            data = get_kline(market, PERIOD(period), limit);
        if data['status'] != 'ok':
            return [];
        datadata = data['data'];
        if period > 60 :
            datadata = ConvertData(60, datadata, period);
        return ConvertKlineData(datadata);

    def getOrder(self, market):
        '''
        ret = self.marketOrders.get(market);
        if ret == None:
            return [];
            'remaining_volume':volume,
            'executed_volume':0,

        for k, o in enumerate(ret):
            data = order_info(o['id']);
            if data['status'] == 'ok':
                data = data['data'];
                o['remaining_volume'] = float(data['amount']) - float(data['field-amount']);
                o['executed_volume'] = float(data['field-amount']);
                o['averageprice'] = float(data['field-cash-amount']) / float(data['field-amount']);
        '''
        data = orders_list(market, "pre-submitted,submitted,partial-filled,partial-canceled,filled,canceled");
        if data['status'] != 'ok':
            return None;
        ret = data['data'];

        for k, o in enumerate(data['data']):
            o['id'] = int(o['id']);
            o['created_at'] = float(o['created-at'])/1000;
            o['side'] = o['type'][0:3];
            if o['side'] != 'buy':
                o['side'] = 'sell';
            o['price'] = float(o['price']);
            o['market'] = o['symbol'];
            o['volume'] = float(o['amount']);
            o['remaining_volume'] = float(o['amount']) - float(o['field-amount']);
            o['executed_volume'] = float(o['field-amount']);
            if o['executed_volume'] > 0:
                o['avg_price'] = float(o['field-cash-amount']) / float(o['field-amount']);
            else:
                o['avg_price'] = 0;
            # pre-submitted,submitted,partial-filled,partial-canceled,filled,canceled
            if o['state'] == "canceled" or o['state'] == 'partial-canceled':
                o['state'] = "cancel";
            if o['state'] == 'filled':
                o['state'] = 'compelete';
        return ret;


    def doOrder(self, market, side, price, volume, time=None, ext=None):
        volume = self.getVolume(market, volume);
        price = self.getPrice(market, price);
        if volume <= 0:
            Log.d("\t\tvolume in precision is nil");
            return True, price, volume;
        nside = 'buy-limit';
        if side == 'sell':
            nside = 'sell-limit';
        result = send_order(volume, 'api', market, nside, price);
        if result['status'] != 'ok':
            Log.d('\t\tdo order result {0}'.format(result));
            return False, price, volume;
        # self.createOrder(result['data'], market, side, price, volume, time, ext);
        return True, price, volume;

    def doOrderCancel(self, orderID, market):
        data = cancel_order(orderID);
        if data['status'] != "ok":
            return False;
        return True;


class huobiEXLocal():

    def set(self, access, secret):
        set_user_key(access, secret)
        self.accounts = {
            'usdt' : {'currency':'usdt', 'balance':'%d' % RebotConfig.user_initamount, 'locked':'0.0'},
        };
        self.orders = {};
        self.marketOrders = {};
        self.ORDERID = 0;
        self.kss = {};
        self.allMarkets = None;
        self.currentMarkets = None;
        self.poundage = 0;#0.0001;
        self.precisions = {};

    def getPrice(self, market, price):
        d = self.precisions[market];
        if d != None:
            return round(price, int(d['price-precision']));
        else :
            return round(price, 0);
    def getVolume(self, market, vol):
        d = self.precisions[market];
        if d != None:
            return Cut(vol, int(d['amount-precision']));
        else :
            return Cut(vol, 0);

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
        currency = market[0:len(market) - len(RebotConfig.base_currency)];

        o['remaining_volume']=0;
        o['executed_volume']=o['volume'];
        o['state']='done';

        if o['side'] == 'sell':
            c = self.accounts.get(currency);
            balance = float(c['balance']);
            c['balance'] = str(balance - o['executed_volume']);
            ccny = self.accounts.get(RebotConfig.base_currency);
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

            ccny = self.accounts.get(RebotConfig.base_currency);
            ccny['balance'] = str(float(ccny['balance']) - addbalance*addprice);

    # function
    def loadData(self, period, timestamp):
        return None;

    def prepare(self, period, timestamp):
        d = get_symbols();
        for k,v in enumerate(d['data']):
            if v['quote-currency'] == 'usdt':
                self.precisions[v['base-currency'] + 'usdt'] = v;

    def getServerTimestamp(self):
        return time.time();

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

        data = get_symbols();
        return data;
        #return [{'id':'anscny'},{'id':'btccny'}, {'id':'ethcny'}, {'id':'zeccny'}, {'id':'qtumcny'}, {'id':'gxscny'}, {'id':'eoscny'}, {'id':'sccny'}, {'id':'dgdcny'}, {'id':'1stcny'}, {'id':'btscny'}, {'id':'gntcny'}, {'id':'repcny'}, {'id':'etccny'}];
        #return [{'id':'anscny'}];

    def getK(self, market, limit, period, timestamp=None):
        if RebotConfig.rebot_is_test == False:
            data = None;
            if period > 60:
                data = get_kline(market, PERIOD(period), limit * period / 60);
            else:
                data = get_kline(market, PERIOD(period), limit);
            if data['status'] != 'ok':
                return [];
            datadata = data['data'];
            if period > 60 :
                datadata = ConvertData(60, datadata, period);
            return ConvertKlineData(datadata);

        ks = self.kss.get(market);
        if ks==None:
            data = None;
            if period > 60:
                data = get_kline(market, PERIOD(period), RebotConfig.rebot_test_k_count * period / 60);
            else:
                data = get_kline(market, PERIOD(period), RebotConfig.rebot_test_k_count);
            datadata = data['data'];
            if period > 60 :
                datadata = ConvertData(60, datadata, period);

            print "kline length", len(datadata), RebotConfig.rebot_test_k_count;
            self.kss[market] = ConvertKlineData(datadata);
            ks = self.kss.get(market);
            # time.sleep(0.01);
        # print timestamp, len(ks), ks[-1][0]
        if ks == None or len(ks) == 0:
            print '%s do not find kline' % market
        if timestamp > ks[-1][0]:
            print '{0} k line is over'.format(market);
            return [];
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
        price = self.getPrice(market, price);
        volume = self.getVolume(market, volume);
        id = self.createOrder(market, side, time, price, volume, ext)
        if id:
            self.compeleteOrder(id);
        return True, price, volume;
    def doOrderCancel(self, orderID, market):
        return None;
