
from formula.K import KLine
from formula.MACD import MACD
from RebotConfig import RebotConfig
from rule.WaveKline import WaveKline
from rule.WavePoint import WavePoint
from rule.WaveKline import Direction

from Log import Log
from formula.Formula import *

import time
import math
import csv

class Mood():
    def __init__(self, ValueN=10):
        self.KLines = KLine();
        self.Value = [];
        self.Volume = [];
        self.ValueN = ValueN;
        self.status = None;
        self.statuscost = 0;
        self.statusbuycurrent = 0;
        self.statusdelay = 0;
        self.stats = [];
        self.High = [];
        self.Low = [];
        self.lastidx = 0;

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
        return;

    def Run(self, d, period=None, servertimestamp=None):
        if len(d) == 0:
            return ;
        self.lastidx = self.KLines.Input(d);

        MA(self.KLines.prices, self.Value, self.ValueN);
        MA(self.KLines.volumes, self.Volume, self.ValueN);
        HIGH(self.KLines.prices, self.High, self.ValueN*2);
        LOW(self.KLines.prices, self.Low, self.ValueN*2);
        if len(self.KLines) > self.ValueN + 1:
            return self.Do();
        return {'type':None};

    def Do(self, idx=-1, ignore=False):
        prek = self.KLines.Get(idx - 1);
        prevolume = self.Volume[idx - 1];
        prevalue = self.Value[idx - 1];

        k = self.KLines.Get(idx);
        value = self.Value[idx];
        volume = self.Volume[idx];
        phigh = self.High[-2];
        plow = self.Low[-2];

        ret = {};

        ret['type'] = None;
        ret['k']    = k;
        ret['sort'] = 1;
        ret['angle'] = 10;
        ret['ext'] = {'idx':idx}

        statslen = len(self.stats)
        for i in range(0, statslen):
            nk = statslen - i - 1;
            arr = self.stats[nk];
            if len(arr) < 5:
                arr.append({'k':k, 'value':value, 'volume':volume});

        self.stats.append([]);

        dv = 1;
        # print "xxxx", self.lastidx, self.statusbuycurrent, self.statusdelay, self.status;
        if self.status == 'buy':
            dv = (self.statuscost - self.statusbuycurrent)/self.statuscost * 2 + 1;
            scale = (self.statuscost - k.c)/self.statuscost > MAXBETA * dv;
            delay = (self.lastidx - self.statusdelay) > MAXKCOUNT * dv;
            # print (self.statuscost - k.c)/self.statuscost, MAXBETA * dv, dv, self.statusdelay, MAXKCOUNT * dv, prek.c > prevalue, prek.vol / (VOLTIMES * prevolume);
            if scale or delay:
                ret['type'] = 'sell';
                ret['ext'] = {
                    'idx'   : idx,
                    'dv'    : dv,
                    'scale' : scale,
                    'delay' : delay,
                }
                return ret;

            if self.statuscost < k.h :
                self.statuscost = k.h;

        #if prek.vol > VOLTIMES * prevolume:
        #    print prek.c, prevalue, prek.c > prevalue, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(prek.t));
        # if (prek.c > prevalue and prek.vol > VOLTIMES * prevolume * dv) or (k.c > value and k.vol > VOLTIMES * volume * dv): #and k.c > phigh :#and k.vol < 3.5 * volume:
        if (k.c > value and k.vol > VOLTIMES * volume * dv) and self.statusdelay != self.lastidx: #and k.c > phigh :#and k.vol < 3.5 * volume:
            ret['type'] = 'buy'
            self.status = 'buy';
            ret['ext']['close'] = (k.c - value) / value * 100
            ret['ext']['voltimes'] = k.vol / volume;

            if self.statusbuycurrent == 0:
                self.statuscost = k.c;
                self.statusbuycurrent = k.c;
                self.statusdelay = self.lastidx;
            else:
                self.statusdelay = self.lastidx + (self.lastidx - self.statusdelay) / 3;
            return  ret;

        return ret;
    def OrderResult(self, ret, orderresult):
        Log.d('\t\torder result, self status {0}, result type {1}, order result {2}'.format(self.status, ret['type'], orderresult));
        if ret['type'] == 'sell':
            if orderresult:
                self.status = 'sell';
                self.statuscost = 0;
                self.statusdelay = 0;
                self.statusbuycurrent = 0;

