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

class TrutleStatA2C():
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
        self.Pool = [];
        self.RecordPools = [];

        for k,v in enumerate(self.markets):
            market = v['id'];
            dk = self.exchange.getK(market, 15, self.period, RebotConfig.rebot_test_begin);
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
            if len(dk) == 0:
                continue;
            ret = r.Run(dk, self.period, self.currenttimestamp);
            if ret != None:
                ret['market'] = market;
                if ret['result'] == 2:
                    Pool.append(ret);
            if len(dk) > 0:
                rest = False;

        Log.d(time.strftime('%Y-%m-%d', time.localtime(self.currenttimestamp)));
        Pool.sort(key=lambda v: v['vol_rate'], reverse=False)
        if rest == False:
            poolsLen = len(self.RecordPools);
            for k in range(-5,0):
                if abs(k) >= poolsLen:
                    break;
                rp = self.RecordPools[k];
                pl = rp['Pool'];
                Profits = rp['Profits']
                ll = 0;
                hh = 0;
                avergp = 0;
                sratio = 0;
                if len(pl) > 0:
                    cc = 0;
                    for k1, v in enumerate(pl):
                        r = self.rules[v['market']];
                        kk = r.KLines[-1 + k];
                        inc = round((r.KLines[-1].c - kk.c)/kk.c * 100, 2);
                        hh = max(hh, inc);
                        ll = min(ll, inc);
                        avergp += inc;
                        if inc > 0:
                            cc +=1;
                    sratio = round(cc/(float)(len(pl))*100,2);
                    avergp = round(avergp / len(pl),2);
                Profits.append({('avergp%d' % k) : avergp, 'sratio%d'%k : sratio, 'hh%d' %k : hh, 'll%d'%k: ll});

            self.RecordPools.append({'time' : time.strftime('%Y-%m-%d', time.localtime(self.currenttimestamp)), 'Pool' : Pool, 'Profits' : []});
            self.Pool = Pool;

        if len(Pool) > 0:
            #print "message", time.strftime('%Y-%m-%d', time.localtime(self.currenttimestamp));
            mks = [];
            for k, v in enumerate(self.Pool):
                mks.append(v['market']);
            Log.d(mks);
            #print '\t', Pool;
        if self.currenttimestamp > time.time():
            stop = True;
        return stop;


    def Export(self, path):
        f = open(path, 'wb');
        w = csv.writer(f);
        w.writerow(['time'
        , 'avergp1', 'sratio1', 'hh1', 'll1'
        , 'avergp2', 'sratio2', 'hh2', 'll2'
        , 'avergp3', 'sratio3', 'hh3', 'll3'
        , 'avergp4', 'sratio4', 'hh4', 'll4'
        , 'avergp5', 'sratio5', 'hh5', 'll5']);
        for k, v in enumerate(self.RecordPools):
            d = [];
            d.append(v['time']);
            Profits = v['Profits'];
            print Profits;
            if len(Profits) > 0:
                for i in range(1, len(Profits) + 1):
                    pv = Profits[i-1];
                    if pv.has_key('avergp-%s'%i) :
                        d.append(Profits[i-1]['avergp-%s'%i]);
                        d.append(Profits[i-1]['sratio-%s'%i]);
                        d.append(Profits[i-1]['hh-%s'%i]);
                        d.append(Profits[i-1]['ll-%s'%i]);
                    else:
                        d.append('0');
                        d.append('0');
                        d.append('0');
            w.writerow(d);
        f.close();
