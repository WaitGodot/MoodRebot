import time
import sys
import socket
import threading

from Log import Log
from Time import Time

from RebotConfig import RebotConfig
from statis.TrutleStatA2B import TrutleStatA2B
from statis.TrutleStatB2C import TrutleStatB2C

STATUS = "running";
stop = 'stop'
socket.setdefaulttimeout(60);

def RunA2B():
    Log.d('\nA2B rebot %s' % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(Time.Time())));
    r = TrutleStatA2B(RebotConfig.rebot_period);
    t = 0;
    while True:
        global STATUS;
        if STATUS == 'stop':
            break;
        t += 1;
        # print "rebot status %s, do %d, time : %s" % (STATUS, t, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(Time.Time())));
        stop = r.Run();
        #print '------------------------------------------------------------------------'
        if RebotConfig.rebot_is_test:
            if t > RebotConfig.rebot_test_k_count or stop == True:
                break;
        else:
            print 'sleep time', RebotConfig.rebot_period*60/RebotConfig.rebot_do_per_period;
            time.sleep(RebotConfig.rebot_period*60/RebotConfig.rebot_do_per_period);
    r.Export('%saa.csv' % RebotConfig.path);

def RunB2C():
    Log.d('\nB2C rebot %s' % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(Time.Time())));
    r = TrutleStatB2C(RebotConfig.rebot_period, '%saa.csv' % RebotConfig.path);
    #refresh data.
    while True:
        global STATUS;
        if STATUS == 'stop':
            break;
        stop = r.Run();
        if stop:
            break;
    r.Export('%sbb.csv' % RebotConfig.path);

if __name__ == "__main__":

    if len(sys.argv) > 1:
        RebotConfig.data_need_load = False;
    else:
        RebotConfig.data_need_load = False;
    # RunA2B();
    RunB2C();