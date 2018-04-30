import time
import urllib2
import sys
import socket
import threading

from exchange.Exchange import Exchange
from exchange.yunbiEX import yunbiEX
from exchange.huobiEX import huobiEX
from exchange.chbtcEX import chbtcEX

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

from Time import Time
from Log import Log

print time.time();
print time.strftime("%H", time.localtime(1520411520));

def f():
    return 1,2,3;
x,y,z = f();
print x,y,z;
def cut(num,c):
    s = '{:.9f}'.format(num);
    pos = s.find('.');
    if pos > 0:
        print pos, s[0:pos+c+1], c, 'xxx', s,num;
        return float(s[0:pos+c+1]);
    else:
        return num;

print cut(0.299, 2)
print cut(299, 2)
print cut(0.299, 5)
print cut(1.234567890,4);
print cut(0.0000012345,4);
print (time.time()-time.time()+1 )/(60*5), time.time()
#'''
exchange = Exchange(RebotConfig.access_key, RebotConfig.secret_key)
exchange.delegate(huobiEX());
exchange.prepare(None, None)
print exchange.doOrder('etcusdt','buy', 30, 0.2000)
#'''
'''
x = [311, 308.5, 304.11, 305.50, 304.51, 308.86, 305.96, 306.07, 308.1, 308.6, 310.99];
y = [];
MA(x, y, 21);
print y;
exchange = Exchange(RebotConfig.access_key, RebotConfig.secret_key);
exchange.delegate(chbtcEX());
'''
#print exchange.getServerTimestamp();
#print exchange.getUser();
# print exchange.getK('btccny', 2, 60, 1504598400000);
#print exchange.getOrder('btscny');
#print exchange.doOrder('btscny', 'buy', 0.1, 100);
#print exchange.getOrder('btscny');
#print exchange.doOrderCancel(2017090420479642, 'btscny');
#print exchange.getOrder('btscny');
