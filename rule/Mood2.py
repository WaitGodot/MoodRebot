
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

class Mood2():
    def __init__(self):
        self.KLines = KLine();
        self.lastidx = -1;
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
        lastidx = self.KLines.Input(d);
        # ret = { "success" : False, "increase_1" : 0,  "increase_2" : 0, 'increase_3' : 0};

        if len(self.KLines) < 10:
            return None;

        kNeg4 = self.KLines[-4];
        kNeg3 = self.KLines[-3];
        kNeg2 = self.KLines[-2];
        kNeg1 = self.KLines[-1];

        kStatNeg7 = self.KLines.Stat(-7);
        kStatNeg6 = self.KLines.Stat(-6);
        kStatNeg5 = self.KLines.Stat(-5);
        kStatNeg4 = self.KLines.Stat(-4);
        kStatNeg3 = self.KLines.Stat(-3);
        kStatNeg2 = self.KLines.Stat(-2);
        kStatNeg1 = self.KLines.Stat(-1);

        oi = (kNeg3.o - kNeg4.c) / kNeg4.c * 100;
        if kStatNeg7 <= 2 and kStatNeg6 >= 3 and kStatNeg5 >= 3 and kStatNeg4 >= 3 and oi >= 2:
            ret = {};
            ret["success"] = False if kStatNeg4 >= 3 else True;
            ret["increase_1"] = round((kNeg3.c - kNeg4.h) / kNeg4.h, 2);
            ret["increase_2"] = round((kNeg2.c - kNeg4.h) / kNeg4.h, 2);
            ret["increase_3"] = round((kNeg1.c - kNeg4.h) / kNeg4.h, 2);
            return ret;
        return None;

    def OrderResult(self, ret, orderresult):
        return None;

