# rule
#
#
from formula.K import KLine
from formula.MACD import MACD
from formula.KDJ import KDJ
from RebotConfig import RebotConfig
from rule.WaveKline import WaveKline
from rule.WavePoint import WavePoint
from rule.WaveKline import Direction

from formula.Formula import *

import time
import math
import csv

class Point():
    def __init__(self, type, idx):
        self.type = type;
        self.idx = idx;
    def __str__(self):
        return 'type:%s,idx:%d' % (self.type, self.idx);

class Wave():
    def __init__(self, point1, point2):
        self.point1 = point1;
        self.point2 = point2;

    def cal(self, ks):
        idx1 = self.point1.idx;
        idx2 = self.point2.idx;
        self.type   = self.point2.type; #'{0}{1}'.format(self.point1.type, self.point2.type);
        self.wmax   = MAX(ks.prices, idx1, idx2);
        self.wmin   = MIN(ks.prices, idx1, idx2);
        self.wvolume    = SUM(ks.volumes, idx1, idx2);
        self.wrmbvolume = SUM(ks.rmbvolumes, idx1, idx2);
        self.winterval  = idx2 - idx1;
        self.cvolume    = ks.volumes[idx2];
        self.crmbvolume = ks.rmbvolumes[idx2];
        self.cprice = ks.prices[idx2];
        self.ck     = ks[idx2];

        # self.height = (self.wmax - self.wmin) * self.winterval;
        self.volheight = self.wrmbvolume / self.winterval;
        self.height = (self.wmax - self.wmin)/self.winterval;
        if self.height == 0:
            self.height = self.winterval;
        if self.volheight == 0:
            self.volheight = self.winterval;

    def __str__(self):
        return 'type={0},idx1={1},idx2={2},height={3},min={4},max={5},cprice={6}'.format(self.type, self.point1.idx, self.point2.idx, self.height, self.wmin, self.wmax, self.cprice);

class MutliMovingAverage():
    def __init__(self, N1=5, N2=10, N3=21, N4=42, N5=84):
        self.KLines = KLine();
        # price
        self.MA1 = [];
        self.MA2 = [];
        self.MA3 = [];
        self.MA4 = [];
        self.MA5 = [];
        self.N1 = N1;
        self.N2 = N2;
        self.N3 = N3;
        self.N4 = N4;
        self.N5 = N5;
        self.status = None;
        # volume
        self.VMA1 = [];
        self.VMA2 = [];
        self.rmbvolumeN3 = 0;
        # points
        self.points = [[], [], []];
        # wave
        self.waves = [[], [], []];
        # trade time
        self.tradeSure = [{'buy':0, 'sell':0}, {'buy':0, 'sell':0}];
        self.tradeidx= 0;
        # kdj
        # self.KDJ = KDJ();

        # ma3 price wave point;
        # self.ma3rate = [];
        # self.wavepointm3 = WavePoint();
        #self.wavewavepointm3 = WavePoint();

    def Run(self, d, period=None, servertimestamp=None):
        if period and servertimestamp:
            data = d[-1];
            x = servertimestamp - data[0];
            if x < period:
                data[5] /= x; # virtual volume
        # k
        self.KLines.Input(d);
        # kdj
        # self.KDJ.Input(self.KLines);
        # price
        lena = len(self.MA1);

        MA(self.KLines.prices, self.MA1, self.N1);
        MA(self.KLines.prices, self.MA2, self.N2);
        MA(self.KLines.prices, self.MA3, self.N3);
        MA(self.KLines.prices, self.MA4, self.N4);
        MA(self.KLines.prices, self.MA5, self.N5);
        # volume
        MA(self.KLines.volumes, self.VMA1, self.N1);
        MA(self.KLines.volumes, self.VMA2, self.N2);

        # ma3 rate and wavepoint;
        # RATE(self.MA3, self.ma3rate, self.N3);
        # self.wavepointm3.InputTrend(self.ma3rate);
        # self.wavewavepointm3.InputTrend(self.wavepointm3.points);

        lenb = len(self.MA2);
        lenc = lenb - lena;
        if lenc >= 2:
            for k in range(lena, lenc - 1):
                self.tradeidx = k;
                self.tradeSure = [{'buy':0, 'sell':0}, {'buy':0, 'sell':0}];
                self.Do(k, True);
        lastk = self.KLines.Get(-1);
        if lastk.idx > self.tradeidx:
            self.tradeSure = [{'buy':0, 'sell':0}, {'buy':0, 'sell':0}];
            self.tradeidx += 1;
        return self.Do();

    def Export(self, path):
        if len(self.MA1) < 1:
            return ;
        f = open(path, 'wb');
        w = csv.writer(f);
        w.writerow(['index', 'MA1', 'MA2', 'MA3', 'MA4']);
        for k in range(0, len(self.MA1)):
            w.writerow([k, self.MA1[k], self.MA2[k], self.MA3[k], self.MA4[k]]);
        f.close();

    def ExportWave(self, path):
        if len(self.waves) < 0:
           return;
        f = open(path, 'wb');
        wcsv = csv.writer(f);
        wcsv.writerow(['index', 'type', 'point1.idx', 'point2.idx', 'wmax', 'wmin', 'wvolume', 'winterval', 'cvolume', 'cprice']);
        for k in range(0, len(self.waves)):
            w = self.waves[k];
            wcsv.writerow([k, w.type, w.point1.idx, w.point2.idx, w.wmax, w.wmin, w.wvolume, w.winterval, w.cvolume, w.cprice]);
        f.close();

    def Do(self, idx=-1, ignore=False):
        ret = {};
        k   = self.KLines.Get(idx);
        type=None;
        pwidx = 0;

        bc43 = CROSS(self.MA4, self.MA3, idx);
        if bc43:
            self.tradeSure[0]['sell'] += 1;
            print "\tma long n3 n4 sell time:{0}, c:{1}, k idx:{2}, sure time:{3}, ignore:{4}".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(k.t)), k.c, k.idx, self.tradeSure[0]['sell'], ignore)
            if ignore or self.tradeSure[0]['sell'] >= RebotConfig.rebot_trade_sure_times:
                self.status = 'sell';
                type = 'sell';
        sc34 = CROSS(self.MA3, self.MA4, idx);
        if sc34:
            self.tradeSure[0]['buy'] += 1;
            print "\tma long n3 n4 buy time:{0}, c:{1}, k idx:{2}, sure time:{3}, ignore:{4}".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(k.t)), k.c, k.idx, self.tradeSure[0]['buy'], ignore)
            if ignore or self.tradeSure[0]['buy'] >= RebotConfig.rebot_trade_sure_times:
                self.status = 'buy'
                type = 'buy';

        if self.status == 'buy' and type == None and False:
            type = self.KDJ.Do();
            if type:
                pwidx = 2;
                print "kdj:{0} time:{1}, c:{2}, k idx:{3}".format(type, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(k.t)), k.c, k.idx)

        if type == None:# and self.status == 'buy':
            bc  = CROSS(self.MA2, self.MA1, idx);
            if bc:
                self.tradeSure[1]['sell'] += 1;
                print "\tma short n1 n2 sell time:{0}, c:{1}, k idx:{2}, sure time:{3}, ignore:{4}".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(k.t)), k.c, k.idx, self.tradeSure[1]['sell'], ignore)
                if ignore or self.tradeSure[1]['sell'] >= RebotConfig.rebot_trade_sure_times:
                    type = 'sell';
                    pwidx = 1;
            sc = CROSS(self.MA1, self.MA2, idx);
            if sc:
                self.tradeSure[1]['buy'] += 1;
                print "\tma short n1 n2 buy time:{0}, c:{1}, k idx:{2}, sure time:{3}, ignore:{4}".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(k.t)), k.c, k.idx, self.tradeSure[1]['buy'], ignore)
                if ignore or self.tradeSure[1]['buy'] >= RebotConfig.rebot_trade_sure_times:
                    type = 'buy';
                    pwidx = 1;
        if type != None:
            # frist update
            points = self.points[pwidx];
            waves = self.waves[pwidx];

            lenwaves    = len(waves);
            lenpoints   = len(points);
            p1wave = None;
            p2wave = None;
            c1wave = None;
            c2wave = None;

            sort = 1000;
            p1 = None;
            p2 = None;

            if lenpoints > 0:
                p2 = points[-1];
                if p2.idx != k.idx:
                    np2 = Point(type, k.idx);
                    if p2.type == type:
                        points[-1] = np2;
                    else:
                        points.append(np2);
                    p2 = np2;
            else:
                p2 = Point(type, k.idx);
                points.append(p2);

            lenpoints = len(points)
            if lenpoints >= 2:
                p1 = points[-2];

            if p1 and p2:
                if lenwaves > 0:
                    c1wave = waves[-1];
                    if c1wave.point2.idx == k.idx:
                        c1wave.cal(self.KLines);
                    if c1wave.type == type:
                        c1wave.point2 = p2;
                        c1wave.cal(self.KLines);
                    else:
                        ncwave = Wave(p1, p2);
                        ncwave.cal(self.KLines);
                        waves.append(ncwave);
                        c1wave = ncwave;
                else:
                    c1wave = Wave(p1, p2);
                    c1wave.cal(self.KLines);
                    waves.append(c1wave);

            if lenwaves >= 4 and pwidx == 1 and True:
                if self.status != 'buy' and False:
                    type = None;
                else:
                    c2wave = waves[-3];
                    p1wave = waves[-2];
                    p2wave = waves[-4];
                    if type == 'buy':
                        type = None;
                        sort = -215
                        if c1wave.wmin > c2wave.wmax:
                            sort = c2wave.height/c1wave.height + c2wave.volheight/c1wave.volheight + p2wave.height/p1wave.height + p2wave.volheight/p1wave.volheight;
                            # print c1wave
                            # print c2wave
                            # print 'buysort', sort, c2wave.height/c1wave.height, c2wave.volheight/c1wave.volheight, p2wave.height/p1wave.height, p2wave.volheight/p1wave.volheight, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(k.t));
                            if sort < 4 :#and p2wave.height/p1wave.height <= 1:
                                type = 'buy';
                                # print '\t short ma wave buy sucess';
                            else:
                                print ' !!! wave buy sort %f, time:%s' % (sort, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(k.t)));
                        else:
                            print ' !!! wave buy c1wave wwin less c2wave wmax';

                    if type == 'sell':
                        # print '\tc1wave', c1wave
                        # print '\tc2wave', c2wave
                        if c1wave.cprice > c2wave.wmax:
                            type = None;
                            print '\t !!! wave sell fail current price greater c2wave wmax time:{0}'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(k.t)));
                        else:
                            print '\t short ma wave sell sucess';

            if pwidx == 0 or type == 'sell': # long long
                sort = 1;
            if type == 'buy' and len(self.points[0]) >= 2:
                p1 = self.points[0][-1];
                p2 = self.points[0][-2];
                # print 'tan p1 p2', 57.2956 * math.atan( (self.MA4[p2.idx] - self.MA4[p1.idx])/self.MA4[p1.idx] * 100 /(p1.idx - p2.idx)), (self.MA4[p2.idx] - self.MA4[p1.idx])/self.MA4[p1.idx] * 100 /(p1.idx - p2.idx);
                # print 'tan c p1', 57.2956 * math.atan( (self.MA4[k.idx] - self.MA4[p1.idx])/self.MA4[p1.idx] * 100/(k.idx - p1.idx)), (self.MA4[k.idx] - self.MA4[p1.idx])/self.MA4[p1.idx] * 100/(k.idx - p1.idx);
                # sort = self.MA4[p.idx] / self.MA4[-1];

                if self.MA4[-1] - self.MA4[p1.idx] < 0 and pwidx != 0:
                    sort = -sort;

                if k.idx - p1.idx > 0:
                    ret['angle'] = 57.2956 * math.atan( (self.MA4[p2.idx] - self.MA4[p1.idx])/self.MA4[p1.idx] * 100 /(p1.idx - p2.idx)) + 57.2956 * math.atan( (self.MA4[k.idx] - self.MA4[p1.idx])/self.MA4[p1.idx] * 100/(k.idx - p1.idx))
                else:
                    ret['angle'] = 57.2956 * math.atan( (self.MA4[p2.idx] - self.MA4[p1.idx])/self.MA4[p1.idx] * 100 /(p1.idx - p2.idx));

                ret['angle'] = 10;
                sort = 1;
                
                # ma5v = self.MA5[p1.idx] - self.MA5[p2.idx];
                ma5v = self.MA5[-1] - self.MA5[p2.idx]
                #if ma5v < 0:
                #    sort = -214;
                #    print '\t !!! ma5 buy less 0:{0}'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(k.t)));

            ret['type'] = type;
            ret['k']    = k;
            ret['sort'] = sort;
            ret['ext'] = {'idx':pwidx}
        if type != None:
            self.tradeSure[pwidx][type] = -RebotConfig.rebot_do_per_period;
        return ret;



