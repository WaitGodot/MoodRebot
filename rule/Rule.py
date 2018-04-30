# rule
from formula.K import KLine
from formula.MACD import MACD
from formula.KDJ import KDJ
from formula.Formula import CROSS
from RebotConfig import RebotConfig
from rule.WaveKline import WaveKline
from rule.WavePoint import WavePoint
from rule.WaveKline import Direction

import time;


class Rule():
    def __init__(self, market, period):
        self.market = market;
        self.period = period;
        self.KLines = KLine();
        self.MACD = MACD();
        self.KDJ = KDJ();
        self.WaveKline = WaveKline();
        self.WaveMACD_DIFF = WavePoint();
        self.WaveMACD_DEA = WavePoint();
        self.WaveMACD_MACD = WavePoint();
        self.WaveKDJ_K = WavePoint();
        self.WaveKDJ_D = WavePoint();

        # self.client = Client(access_key=RebotConfig.access_key, secret_key=RebotConfig.secret_key)
        self.begin = 0;

    def Run(self, d):
        # d = self.client.get(get_api_path('k'), params={'market': '{0}cny'.format(self.market), 'limit':100,'period' : '{0}'.format(self.period)});
        # print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(d[0][0]));
        self.KLines.Input(d);
        self.MACD.Input(self.KLines);
        self.KDJ.Input(self.KLines);

        self.WaveKline.Input(self.KLines);
        self.WaveMACD_DIFF.Input(self.MACD.DIFF);
        self.WaveMACD_DEA.Input(self.MACD.DEA)
        self.WaveKDJ_K.Input(self.KDJ.K);
        self.WaveKDJ_D.Input(self.KDJ.D);
        klen = len(self.KLines);
        self.begin  = klen;

        # self.WaveKline.Export("C:\\Users\\randy\\k.csv");

    # macd diff, dea 0 de daxiao   
    def Trend(self): 
        lmacd = len(self.MACD);
        if lmacd < 2:
            return Direction.FLAT;
        if self.MACD.DIFF[lmacd-1] >= 0 and self.MACD.DIFF[lmacd-2] >= 0 and self.MACD.DEA[lmacd-1] >= 0 and self.MACD.DEA[lmacd-2] >=0:
            return Direction.UP;

        return Direction.DOWN;
    def Do(self):
        d = self.Trend();
        kc = self.WaveKline.Get(-1);
        kp = self.WaveKline.Get(-2, kc.dir);
        k = self.KLines.Get(-1);
        klen = len(self.KLines);
        if kc.hkidx < 0 or kc.lkidx < 0 or kp == None:
            return None;
        
        # print 'kc:',kc,'kp:',kp
        # print kp.hk.c, kc.hk.c, kp.lk.c, kp.lk.c

        if kp.hk.h <= kc.hk.h and kp.hk.c > kc.lk.c:
            # 
            # print "\n"
            # print kp.hk.c, kc.hk.c, kc.lk.c
            # print 'kc:',kc,'kp:',kp

            ktrend = self.WaveKline.TrendWeaken();
            macdtrend = self.WaveMACD_DIFF.TrendWeaken(kc.dir);
            kdjkseg = self.WaveKDJ_K.Get(-1);
            #if ktrend:
                # print "sell", klen-1, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(k.t)), d, ktrend, macdtrend, kdjkseg.dir
            # sell
            if ktrend and macdtrend and kdjkseg.dir == Direction.DOWN:
                return 'sell';
        if kp.lk.c > kc.lk.c and kp.lk.c < kc.hk.c:
            # 
            ktrend = self.WaveKline.TrendWeaken();
            macdtrend = self.WaveMACD_DIFF.TrendWeaken(kc.dir);
            kdjkseg = self.WaveKDJ_K.Get(-1);
            #if ktrend:
                # print "buy", klen-1, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(k.t)), ktrend, macdtrend, kdjkseg.dir

            # buy
            if ktrend and macdtrend and kdjkseg.dir == Direction.UP:
                return 'buy';
        return None


        
