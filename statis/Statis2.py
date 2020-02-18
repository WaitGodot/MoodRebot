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

from rule.Mood2 import Mood2

from Time import Time
from Log import Log

class Statis2():
    def __init__(self, period):
        self.period = period;
        self.exchange = Exchange(RebotConfig.access_key, RebotConfig.secret_key);
        delegate = None;
        if RebotConfig.exchange == 'chbtc':
            if RebotConfig.rebot_release:
                delegate = chbtcEX();
            else:
                delegate = chbtcEXLocal();
        if RebotConfig.exchange == 'yunbi':
            if RebotConfig.rebot_release:
                delegate = yunbiEX();
            else:
                delegate = yunbiEXLocal();
        if RebotConfig.exchange == "tushare":
            delegate = tushareEXLocal();
        if RebotConfig.exchange == "huobi":
            if RebotConfig.rebot_release:
                delegate = huobiEX();
            else:
                delegate = huobiEXLocal();

        self.exchange.delegate(delegate);
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
        for k,v in enumerate(self.markets):
            market = v['id'];

            if RebotConfig.rebot_is_test:
                dk = self.exchange.getK(market, 42, self.period, RebotConfig.rebot_test_begin); # 1498838400:2017/7/1 0:0:0; 1496246400:2017/6/1 0:0:0; 1493568000:2017/5/1 0:0:0
            else:
                dk = self.exchange.getK(market, 500, self.period);

            r = Mood2();
            r.Run(dk);

            lastk = r.KLines.Get(-1);
            self.rules[market] = r;
            if lastk:
                self.currenttimestamp = lastk.t;
            #    Log.d('index:%d, start market:%s, begin time %s, current time:%s'%(k, market, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(r.KLines.Get(0).t)), time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(lastk.t))));
        self.zuorizhangting = {};
        self.datas = [];

    def run(self):
        # print '-----------------------------------------------------------------'
        stop = False;
        rest = True;
        # markets
        nmarkets = self.exchange.getMarkets()
        if nmarkets:
            self.markets = nmarkets;

        data = {};
        stats = [];

        self.currenttimestamp = self.exchange.getNextKTime(self.period, self.currenttimestamp);
        for k,v in enumerate(self.markets):
            market = v['id'];
            r   = self.rules[market];
            dk  = self.exchange.getK(market, 1, self.period, self.currenttimestamp);
            ret = r.Run(dk, self.period, self.currenttimestamp);
            if ret != None:
                ret['market'] = market;
                stats.append(ret);
            if len(dk) > 0:
                rest = False;
        if rest :
            print 'rest', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.currenttimestamp))

        sucessRatio = 0;
        avgIncrease1 = 0;
        minIncrease1 = 100;
        maxIncrease1 = 0;
        avgIncrease2 = 0;
        minIncrease2 = 100;
        maxIncrease2 = 0;
        avgIncrease3 = 0;
        minIncrease3 = 100;
        maxIncrease3 = 0;

        jinrizhangting = {};
        for k, v in enumerate(stats):
            sucessRatio = sucessRatio + v["success"];
            avgIncrease1 = avgIncrease1 + v["increase_1"];
            avgIncrease2 = avgIncrease2 + v["increase_2"];
            avgIncrease3 = avgIncrease3 + v["increase_3"];
            minIncrease1 = min(minIncrease1, v["increase_1"]);
            minIncrease2 = min(minIncrease2, v["increase_2"]);
            minIncrease3 = min(minIncrease3, v["increase_3"]);
            maxIncrease1 = max(maxIncrease1, v["increase_1"]);
            maxIncrease3 = max(maxIncrease2, v["increase_2"]);
            maxIncrease2 = max(maxIncrease3, v["increase_3"]);
            
        sc = len(stats);
        data['time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.currenttimestamp));
        data["count"] = sc;
        if sc > 0:
            data['sucessRatio'] = round(sucessRatio / (float)(sc), 2);
            data["avgIncrease1"] = round(avgIncrease1 / sc, 2);
            data["avgIncrease2"] = round(avgIncrease2 / sc, 2);
            data["avgIncrease3"] = round(avgIncrease3 / sc, 2);
        else:
            data['sucessRatio'] = 0
            data["avgIncrease1"] = 0
            data["avgIncrease2"] = 0
            data["avgIncrease3"] = 0
            minIncrease1 = 0;
            minIncrease2 = 0;
            minIncrease3 = 0;
        data["minIncrease1"] = minIncrease1;
        data["minIncrease2"] = minIncrease2;
        data["minIncrease3"] = minIncrease3;
        data["maxIncrease1"] = maxIncrease1;
        data["maxIncrease2"] = maxIncrease2;
        data["maxIncrease3"] = maxIncrease3;
        if not rest and sc > 0:
            self.datas.append(data);
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
