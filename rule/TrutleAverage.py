
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

class TrutleAverage():
    def __init__(self):
        self.KLines = KLine();
        self.lastidx = -1;
        self.data = [];
        self.MA = [];
        self.N = 10;
        self.HHVVol = [];
        self.LimitAmount = 1 * 100000000;

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
        lastidx = self.KLines.Input(d);
        ret = { 'result' : 0, 'vol_rate' : 0, 'rate' : 0};
        if len(self.KLines) < self.N:
            return ret;

        MA(self.KLines.prices, self.MA, self.N);
        if self.KLines[-1].amount < self.LimitAmount:
            return ret;
        if not self.CheckCurentKLegal():
            return ret;
        cals = self.CalIntervalIncreaseLegal();
        if not cals[0]:
            return ret;

        count = cals[1];
        hkidx = cals[2];
        hlamplitude = cals[3];

        hlimitcount = 0;
        for i in range(1, count):
            if self.KLines.Stat(-i) == 3:
                hlimitcount += 1;
        if hlimitcount < 3:
            return ret;

        hhvVol = [];
        HIGH(self.KLines.volumes, hhvVol, count);
        ck = self.KLines[-1];
        rate = round(ck.vol / hhvVol[-1], 2);
        if  rate <= 0.5 :
            ret['result'] = 1;
        ret['vol_rate'] = rate;
        ret['rate'] = hlimitcount + 1 - rate;
        # print ret, cals, rate, hlimitcount, type(ret['rate']);
        return ret;

    def CheckCurentKLegal(self):
        ck = self.KLines[-1];
        ll = ck.l * 0.97;
        hh = ck.h;
        if self.MA[-1] < ll or self.MA[-1] > hh:
            return False;
        return True;

    def CalIntervalIncreaseLegal(self):
        c = 2;
        hc = 0;
        lc = 100000;
        hidx = -2;
        while c < len(self.KLines):
            cck = self.KLines[-c];
            if cck.c < self.MA[-c]:
                break;
            else:
                if cck.h > hc:
                    hc = cck.h;
                    hidx = -c;
                if cck.l < lc:
                    lc = cck.l;
                c = c+1;
        icv = (hc - lc) / lc;
        if icv < 0.33:
            return [False];
        return [True, c, hidx, icv];

    def OrderResult(self, ret, orderresult):
        return None;

