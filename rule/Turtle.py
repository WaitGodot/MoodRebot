
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

class Turtle():
    def __init__(self):
        self.KLines = KLine();
        self.lastidx = -1;
        self.data = [];
        self.MA23 = [];
        self.HHVVol = [];
        self.LimitAmount = 5 * 100000000;

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
        ret = { "result" : 0, "vol_rate" : 0};

        if len(self.KLines) < 21:
            return ret;

        RecordIdx = -1;
        MA(self.KLines.prices, self.MA23, 23);
        for i in range(1, 21):
            idx = -i;
            kidx = self.KLines[idx];
            kpreidx = self.KLines[idx-1];
            if (kidx.c - kpreidx.c) / kpreidx.c > 0.08 and kidx.c > self.MA23[idx] and kidx.amount >= self.LimitAmount:
                RecordIdx = idx;
                break;

        if RecordIdx == -1:
            return ret;
        
        KRecored = self.KLines[RecordIdx];
        for idx in range(RecordIdx, 0):
            if self.KLines[idx].c < KRecored.c * 0.93:
                return ret;
        ret['result'] = 1;

        hhvVol = [];
        HIGH(self.KLines.volumes, hhvVol, 23);
        ck = self.KLines[-1];
        pk = self.KLines[-2];
        rate = round(ck.vol / hhvVol[-1], 2);
        increase = round(abs((ck.c - pk.c)/pk.c),4);
        if  rate <= 0.45 and ck.amplitude <= 0.04 and increase <= 0.03 and round(abs((ck.c - ck.o)/ck.o),4) < 0.015:
            ret['result'] = 2;
        ret['vol_rate'] =  rate;
        ret['amplitude'] =  round(ck.amplitude,2);
        ret['increase'] = increase;
        # print rate, round(KRecored.amplitude, 2), time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(KRecored.t)), time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(servertimestamp)), ret['result'];

        return ret;

    def OrderResult(self, ret, orderresult):
        return None;

