import tushare as ts
import time
import pandas

class Client():
    def loadData(self, period, timestamp):
        print 'load data start'
        self.kdatas = {};
        pdata = ts.get_today_all();
        pdata.to_string(columns=['code'],index=False)
        data = pdata.values.tolist();
        self.kdatas['market'] = pdata;
        pdata.to_csv('./data/market.csv', index=False, columns = ['code'], encoding='utf-8');
        for k,v in enumerate(data):
            id = str(v[0]);
            key = '%s%s' %(id, period);
            print id, key, period, timestamp
            kd = ts.get_k_data(id, start = timestamp, ktype = period);
            kd.to_csv('./data/%s/%s.csv' % (period, id), index=False);

            self.kdatas[key] = kd;
        print 'load data compelete'

    def prepare(self, period, timestamp):
        print 'prepare data start'
        self.kdatas = {};
        pdata = pandas.read_csv('./data/market.csv');
        data = pdata.values.tolist();
        self.kdatas['market'] = pdata;

        for k,v in enumerate(data):
            id = str(v[0]);
            if len(id) < 6:
                id = '%s%s' % (self.zero(6 - len(id)), id);
            try:
                key = '%s%s' %(id, period);
                kd = pandas.read_csv('./data/%s/%s.csv' % (period, id));
                self.kdatas[key] = kd;
            except Exception as e:
                print '%s load fail!' % id;

        print 'prepare data compelete'

    def time(self):
        return time.time();

    def getK(self, market, period, timestamp):
        key = '%s%s' %(market, period);
        return self.kdatas.get(key);
        # return self.kdatas[key]; #return ts.get_k_data(market, start = timestamp, ktype = period);

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