import time
import urllib2
import math
import csv

from RebotConfig import RebotConfig

from exchange.Exchange import Exchange
from exchange.yunbiEX import *
from exchange.chbtcEX import *
from exchange.tushareEX import *
from exchange.huobiEX import *

from formula.K import *
from formula.MACD import *
from formula.Formula import *

from rule.Turtle import Turtle

from Time import Time
from Log import Log

class TrutleStat():
    def __init__(self, period):
        self.period = period;
        self.exchange = Exchange(RebotConfig.access_key, RebotConfig.secret_key);
        self.exchange.delegate(tushareEXLocal());
        # time
        Time.SetServerTime(self.exchange.getServerTimestamp())
        # data.
        if RebotConfig.data_need_load:
            self.exchange.loadData(period, RebotConfig.rebot_test_begin);
        self.exchange.prepare(period, RebotConfig.rebot_test_begin);

        # markets
        self.markets = self.exchange.getMarkets();
        # rule.
        self.rules = {};
        # init.
        self.currenttimestamp = 0;
        self.datas = [];
        for k,v in enumerate(self.markets):
            market = v['id'];

            if RebotConfig.rebot_is_test:
                dk = self.exchange.getK(market, 1, self.period, RebotConfig.rebot_test_begin); # 1498838400:2017/7/1 0:0:0; 1496246400:2017/6/1 0:0:0; 1493568000:2017/5/1 0:0:0
            else:
                dk = self.exchange.getK(market, 500, self.period);

            r = Turtle();
            r.Run(dk);

            lastk = r.KLines.Get(-1);
            self.rules[market] = r;
            if lastk:
                self.currenttimestamp = lastk.t;
                # Log.d('index:%d, start market:%s, begin time %s, current time:%s'%(k, market, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(r.KLines.Get(0).t)), time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(lastk.t))));

    def run(self):
        # print '-----------------------------------------------------------------'
        stop = False;
        rest = True;
        # markets
        nmarkets = self.exchange.getMarkets()
        if nmarkets:
            self.markets = nmarkets;

        data = {};
        PoolB = [];
        PoolC = [];

        self.currenttimestamp = self.exchange.getNextKTime(self.period, self.currenttimestamp);
        for k,v in enumerate(self.markets):
            market = v['id'];
            r   = self.rules[market];
            dk  = self.exchange.getK(market, 1, self.period, self.currenttimestamp);
            ret = r.Run(dk, self.period, self.currenttimestamp);
            if ret != None:
                ret['market'] = market;
                if ret['result'] == 1:
                    PoolB.append(ret);
                if ret['result'] == 2:
                    PoolC.append(ret);
            if len(dk) > 0:
                rest = False;
        # if rest :
        #    print 'rest', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.currenttimestamp))

        if rest == False and len(PoolC) > 0:
            print 'Order Msg : ', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.currenttimestamp))
            for k,v in enumerate(PoolC):
                print v['market'];
        
        if self.currenttimestamp > time.time():
            stop = True;
        return stop;

    def Export(self, path):
        f = open(path, 'wb');
        w = csv.writer(f);
        w.writerow(['time', 'count', 'sucessRatio', 
        'avgIncrease1', 'minIncrease1', 'maxIncrease1',
        'avgIncrease2', 'minIncrease2', 'maxIncrease2',
        'avgIncrease3', 'minIncrease3', 'maxIncrease3']);
        for k, data in enumerate(self.datas):
            d = [];
            d.append(data['time'])
            d.append(data['count'])
            d.append(data['sucessRatio'])
            d.append(data['avgIncrease1'])
            d.append(data['minIncrease1'])
            d.append(data['maxIncrease1'])
            d.append(data['avgIncrease2'])
            d.append(data['minIncrease2'])
            d.append(data['maxIncrease2'])
            d.append(data['avgIncrease3'])
            d.append(data['minIncrease3'])
            d.append(data['maxIncrease3'])
            w.writerow(d);
        f.close();
