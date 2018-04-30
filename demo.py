import time
import urllib2
import sys
import socket
import threading

from exchange.Exchange import Exchange
from exchange.yunbiEX import yunbiEX

from formula.K import KLine
from formula.MACD import MACD
from formula.Formula import SMA
from formula.Formula import MA
from formula.Formula import EMA
from formula.Formula import HIGH
from formula.Formula import LOW
from RebotConfig import RebotConfig
from rule.Rule import Rule
from rule.MutliMovingAverage import MutliMovingAverage
from user.User import User
from Rebot import Rebot;
from exchange.yunbi.client import Client, get_api_path
from exchange.yunbiEX import yunbiEXLocal
from exchange.huobiEX import huobiEX
from Time import Time
from Log import Log


# 30 60 120 240 360
# btc 120, 60
# ans 60, 240
# eth 120, 360
# omg 240, 120
# zec 240, 60
# qtum 60, 240
# bts 240, 360
# gxs 240, 360
# eos 30, 60
# sc 60, 360
# snt 360, 240
# dgd 360, 240
# 1st 60, 120
# rep 60, 120
# gnt 360, 240
# etc 120, 240
# sys.stdout = open('%s%s' % (RebotConfig.path, RebotConfig.log), 'a+')

STATUS = "running";
stop = 'stop'

socket.setdefaulttimeout(60);
def Done():
    Log.d('\nstart rebot %s' % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(Time.Time())));
    r = Rebot(RebotConfig.rebot_period);
    t = 0;
    while True:
        global STATUS;
        if STATUS == 'stop':
            break;
        t += 1;
        #print "rebot status %s, do %d, time : %s" % (STATUS, t, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(Time.Time())));
        stop = r.run();
        #print '------------------------------------------------------------------------'
        if RebotConfig.rebot_is_test:
            if t > RebotConfig.rebot_test_k_count or stop == True:
                break;
        else:
            print 'sleep time', RebotConfig.rebot_period*60/RebotConfig.rebot_do_per_period;
            time.sleep(RebotConfig.rebot_period*60/RebotConfig.rebot_do_per_period);

    print '\n\norders'
    alltradetimes = 0;
    allwintimes = 0;
    alluncompeletetimes = 0;
    for k,v in enumerate(r.markets):
        market = v['id'];
        ods = r.user.getOrderMarket(market);
        lenods = len(ods);
        if lenods > 0:
            buys = [];
            tradetimes = 0;
            wintimes = 0;
            uncompeletetimes = 0
            Log.d('market:%s' % market);
            key=0;
            for k,v in enumerate(ods):
                if v.type == 'buy':
                    tradetimes += 1;
                    alltradetimes += 1;
                    buys.append(v);
                if v.type == 'sell':
                    Log.d('\t%s' % v);
                    for bk, bv in enumerate(buys):
                        scale = (v.averageprice - bv.averageprice)/bv.averageprice * 100;
                        if scale > 0:
                            wintimes += 1;
                            allwintimes += 1;
                        Log.d('\t\tscale:%s, order:%s' % (scale, bv.__str__()));
                        key = k;
                    buys = [];
            if len(buys) > 0:
                Log.d('\tcurrent buy order:')
                for k,v in enumerate(buys):
                    uncompeletetimes += 1;
                    alluncompeletetimes += 1;
                    Log.d('\t\t%s' % v.__str__());
            if tradetimes - uncompeletetimes > 0 :
                Log.d('\twinner: %f, win: %d, uncompelete %d, all %d\n' % (float(wintimes)/ float(tradetimes - uncompeletetimes) * 100, wintimes, uncompeletetimes, tradetimes));
            else:
                Log.d('\twinner: %f, win: %d, uncompelete %d, all %d\n' % (0, wintimes, uncompeletetimes, tradetimes));
    if alltradetimes <= 0:
        Log.d('none trade')
    else:
        Log.d('all win: %f, win: %d, uncompelete %d, all %d\n' % (float(allwintimes)/ float(alltradetimes - alluncompeletetimes) * 100, allwintimes, alluncompeletetimes, alltradetimes));

    import csv
    f = open('%sscales.csv' % RebotConfig.path, 'wb');
    w = csv.writer(f);
    w.writerow(['scale']);
    for k in range(0, len(r.scales)):
        w.writerow([k, r.scales[k]]);
    f.close();

    for k,v in r.rules.items():
        v.Export('%sma.csv' % RebotConfig.path);


Done();
'''
nr = threading.Thread(target=Done);
nr.start();

while True:
    try:
        STATUS = input('STATUS:');
        if STATUS == 'stop':
            break;
    except Exception:
        print ''
'''
