import tushare as ts
import time
import pandas
from jqdatasdk import *

class Client():
    def __init__(self):
        auth('18521524015', '147Randy');
        print is_auth;

    def loadData(self, period, timestamp):
        print 'load data start'
        self.kdatas = {};
        ts.set_token('0a1fda4e4f21b5871a7b20c7e8e02d573a6290b8189b62e32fc3c73e');
        # pdata = ts.get_today_all();
        # pdata.to_string(columns=['code'],index=False)
        # pdata.to_csv('./data/market.csv', index=False, columns = ['code'], encoding='utf-8');
        pdata = pandas.read_csv('./data/market.csv');
        data = pdata.values.tolist();
        self.kdatas['market'] = pdata;
        for k,v in enumerate(data):
            id = self.nomalize(str(v[0]));
            key = '%s%s' %(id, period);
            # kd = pro.daily(ts_code= '%s%s' % (id, self.exchangeStr(id))); #ts.get_k_data(id, ktype = period);#ts.get_k_data(id, start = timestamp, ktype = period);
            kd = get_bars(normalize_code(id), 200, unit='1d',fields=['date','open','high','low','close','volume','money'],include_now=True)
            print id, key, period, timestamp, k, len(data);
            kd.to_csv('./data/%s/%s.csv' % (period, id), index=False);
            self.kdatas[key] = kd;
            if k == len(data)/2:
                time.sleep(1);
        print 'load data compelete'

    def prepare(self, period, timestamp):
        print 'prepare data start'
        self.kdatas = {};
        pdata = pandas.read_csv('./data/market.csv');
        data = pdata.values.tolist();
        self.kdatas['market'] = pdata;

        for k,v in enumerate(data):
            id = self.nomalize(str(v[0]));
            try:
                key = '%s%s' %(id, period);
                kd = pandas.read_csv('./data/%s/%s.csv' % (period, id));
                self.kdatas[key] = kd;
            except Exception as e:
                print '%s load fail!' % id, e;
        print 'prepare data compelete'
        
    def refresh(self, period, market):
        key = '%s%s' %(market, period);
        kd = get_bars(normalize_code(market), 200, unit='1d',fields=['date','open','high','low','close','volume','money'],include_now=True)
        self.kdatas[key] = kd;

    def time(self):
        return time.time();

    def getK(self, market, period, timestamp):
        key = '%s%s' %(market, period);
        kd = self.kdatas.get(key);
        return kd;
        # return self.kdatas[key]; #return ts.get_k_data(market, start = timestamp, ktype = period);

    # def get_trade_days

    def getMarkets(self):
        data = self.kdatas['market'].values.tolist();
        nd = [];
        for k,v in enumerate(data):
            id = str(v[0]);
            if len(id) < 6:
                id = '%s%s' % (self.zero(6 - len(id)), id);
            nd.append({'id':id});
        return nd;
    def zero(self, count):
        if count == 1:
            return '0';
        if count == 2:
            return '00';
        if count == 3:
            return '000';
        if count == 4:
            return '0000';
        if count == 5:
            return '00000';
    def nomalize(self, id):
        if len(id) < 6:
            id = '%s%s' % (self.zero(6 - len(id)), id);
        return id;
    def exchangeStr(self, code):
        if code[0] == '6':
            return '.SH';
        else:
            return '.SZ';
        