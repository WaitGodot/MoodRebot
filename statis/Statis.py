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

from rule.Mood import Mood

from Time import Time
from Log import Log

class Statis():
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

            r = Mood();
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
            ret['market'] = market;
            stats.append(ret);
            if len(dk) > 0:
                rest = False;
        if rest :
            print 'rest', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.currenttimestamp))

        statsconut = {"-3":0, "-2":0, "-1":0, "0":0, "1":0, "2":0, "3":0};
        maxlimitcount = 0;
        maxlimitmarket = 'None';
        limit2openincrese = 0;
        limit2count = 0;
        limit2increase = 0;

        jinrizhangting = {};
        for k, v in enumerate(stats):
            c = v["stat"];
            limit_count = v['limit_count'];
            market = v['market'];

            statsconut[str(c)] += 1;
            if self.zuorizhangting.get(market):
                limit2openincrese += v['open_increase'];
                limit2increase += v['increase'];
                if c > 0:
                    limit2count += 1;
            if limit_count > 0:
                jinrizhangting[market] = True;
            if maxlimitcount < limit_count:
                maxlimitcount = limit_count;
                maxlimitmarket = market;

        data['time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.currenttimestamp));
        data['ping'] = statsconut['0'];
        data["shangzhang"] = statsconut['3'] + statsconut['2'] + statsconut['1'];
        data['xiadie'] = statsconut['-3'] + statsconut['-2'] + statsconut['-1'];
        data['shangzhanglv'] = float(data["shangzhang"]) / float(data["shangzhang"] + data['xiadie'] + statsconut['0']);
        data["zhangting"] = statsconut["3"];
        data["kaiban"] = statsconut['2'];
        data['dieting'] = statsconut['-3'];
        data['lianbanshu'] = maxlimitcount;
        data['maxlimitmarket'] = maxlimitmarket;

        if statsconut['2'] + statsconut['3'] > 0:
            data['fengbanlv'] = float(statsconut['3']) / float(statsconut['2'] + statsconut['3']);
        else:
            data['fengbanlv'] = 1;

        if statsconut['-3'] > 0:
            data['zhangdietingbi'] = float(statsconut['3']) / float(statsconut['-3']);
        else:
            data['zhangdietingbi'] = 1;

        lenzuorizhangting = len(self.zuorizhangting)
        if lenzuorizhangting > 0:
            data['y_lianbankaipanavg'] = limit2openincrese / lenzuorizhangting / 0.1;
            data['y_lianbanavg'] = limit2increase / lenzuorizhangting / 0.1;
            data['y_shangzhanglv'] = float(limit2count) / float(lenzuorizhangting);
        else:
            data['y_lianbankaipanavg'] = 0;
            data['y_lianbanavg'] = 0;
            data['y_shangzhanglv'] = 0;

        # print data;
        if rest == False:
            self.datas.append(data);
        self.zuorizhangting = jinrizhangting;
        if self.currenttimestamp > time.time():
            stop = True;
        return stop;

    def Export(self, path):
        f = open(path, 'wb');
        w = csv.writer(f);
        w.writerow(['time', 'ping', 'shangzhang', 'xiadie', 'shangzhanglv', 'zhangting', 'kaiban', 'dieting', 'fengbanlv', 'zhangdietingbi', 'lianbanshu', 'maxlimitmarket', 'y_lianbankaipanavg', "y_lianbanavg", "y_shangzhanglv"]);
        for k, data in enumerate(self.datas):
            d = [];
            d.append(data['time'])
            d.append(data['ping'])
            d.append(data['shangzhang'])
            d.append(data['xiadie'])
            d.append(data['shangzhanglv'])
            d.append(data['zhangting'])
            d.append(data['kaiban'])
            d.append(data['dieting'])
            d.append(data['fengbanlv'])
            d.append(data['zhangdietingbi'])
            d.append(data['lianbanshu'])
            d.append(data['maxlimitmarket'])
            d.append(data['y_lianbankaipanavg'])
            d.append(data['y_lianbanavg'])
            d.append(data['y_shangzhanglv'])


            w.writerow(d);
        f.close();
