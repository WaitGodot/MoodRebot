
from RebotConfig import RebotConfig

from formula.K import KLine
from formula.MACD import MACD
from formula.KDJ import KDJ

from rule.WaveKline import *
from rule.WavePoint import WavePoint

from Log import Log
from formula.Formula import *

import time
import math
import csv

class Mood():
    def __init__(self):
        self.KLines = KLine();
        self.lastidx = -1;
        self.limitcount = 0;
        self.data = [];

    def Export(self, path):
        f = open(path, 'wb');
        w = csv.writer(f);
        w.writerow(['increase', 'amplitude', 'close', 'vol', 'value', 'volume', 'increase', 'amplitude', 'close', 'vol', 'value', 'volume', 'increase', 'amplitude', 'close', 'vol', 'value', 'volume', 'increase', 'amplitude', 'close', 'vol', 'value', 'volume', 'increase', 'amplitude', 'close', 'vol', 'value', 'volume']);
        for k, arr in enumerate(self.stats):
            d = [];
            for i in range(0,len(arr)):
                nd = arr[i];
                d.append(nd['k'].increase)
                d.append(nd['k'].amplitude)
                d.append(nd['k'].c)
                d.append(nd['k'].vol)
                d.append(nd['value'])
                d.append(nd['volume'])

            w.writerow(d);
        f.close();

    def Run(self, d, period=None, servertimestamp=None):
        ret = { "stat" : 0, "open_increase" : 0, 'limit_count' : 0};

        lastidx = self.KLines.Input(d);
        if len(self.KLines) < 2:
            return ret;

        if lastidx == self.lastidx:
            return ret;

        k = self.KLines[-1];
        # stat
        stat = self.KLines.Stat();

        # pre
        prek = self.KLines[-2];
        if stat == 3:
            self.limitcount += 1;
        else:
            self.limitcount = 0;

        ret["open_increase"] = (k.o - prek.c) / prek.c;
        ret['limit_count'] = self.limitcount;
        ret["stat"] = stat;

        self.lastidx = lastidx;
        self.data.append(ret);

        return ret;

    def OrderResult(self, ret, orderresult):
        return None;

