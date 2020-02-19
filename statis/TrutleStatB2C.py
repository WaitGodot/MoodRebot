import time
import urllib2
import math
import csv

from RebotConfig import RebotConfig
from exchange.Exchange import Exchange
from exchange.tushareEX import *
from formula.K import *
from formula.MACD import *
from formula.Formula import *

from rule.Turtle import Turtle

from Time import Time
from Log import Log

class TrutleStatB2C():
    def __init__(self, period, path):
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
        f = open(path, 'r');
        r = csv.DictReader(f);
        self.markets = [];
        for row in r:
            id = row['code'];
            self.markets.append({'id':id});
        # rule.
        self.rules = {};
        # init.
        self.currenttimestamp = 0;
        self.Pool = [];
        for k,v in enumerate(self.markets):
            market = v['id'];
            self.exchange.refresh(self.period, market);
            dk = self.exchange.getK(market, 1, self.period, RebotConfig.rebot_test_begin);
            r = Turtle();
            r.Run(dk);
            lastk = r.KLines.Get(-1);
            self.rules[market] = r;
            if lastk:
                self.currenttimestamp = lastk.t;
                # Log.d('index:%d, start market:%s, begin time %s, current time:%s'%(k, market, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(r.KLines.Get(0).t)), time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(lastk.t))));

    def Run(self):
        # print '-----------------------------------------------------------------'
        stop = False;
        rest = True;
        Pool = [];
        self.currenttimestamp = self.exchange.getNextKTime(self.period, self.currenttimestamp);
        for k,v in enumerate(self.markets):
            market = v['id'];
            r   = self.rules[market];
            dk  = self.exchange.getK(market, 1, self.period, self.currenttimestamp);
            ret = r.Run(dk, self.period, self.currenttimestamp);
            if ret != None:
                ret['market'] = market;
                if ret['result'] == 2:
                    Pool.append(ret);
            if len(dk) > 0:
                rest = False;

        Pool.sort(key=lambda v: v['vol_rate'], reverse=False)
        if rest == False:
            self.Pool = Pool;

        if len(Pool) > 0 and False:
            print "message", time.strftime('%Y-%m-%d', time.localtime(self.currenttimestamp));
            print '\t', Pool;
        if self.currenttimestamp > time.time():
            stop = True;
        return stop;


    def Export(self, path):
        f = open(path, 'wb');
        w = csv.writer(f);
        w.writerow(['code']);
        for k, v in enumerate(self.Pool):
            d = [];
            d.append(v['market'])
            w.writerow(d);
        f.close();
