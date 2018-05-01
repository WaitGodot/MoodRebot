import time
import sys
import socket
import threading

from Log import Log
from Time import Time

from RebotConfig import RebotConfig
from statis.Statis import Statis


STATUS = "running";
stop = 'stop'
socket.setdefaulttimeout(60);

def Done():
    Log.d('\nstart rebot %s' % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(Time.Time())));
    r = Statis(RebotConfig.rebot_period);
    t = 0;
    while True:
        global STATUS;
        if STATUS == 'stop':
            break;
        t += 1;
        # print "rebot status %s, do %d, time : %s" % (STATUS, t, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(Time.Time())));
        stop = r.run();
        #print '------------------------------------------------------------------------'
        if RebotConfig.rebot_is_test:
            if t > RebotConfig.rebot_test_k_count or stop == True:
                break;
        else:
            print 'sleep time', RebotConfig.rebot_period*60/RebotConfig.rebot_do_per_period;
            time.sleep(RebotConfig.rebot_period*60/RebotConfig.rebot_do_per_period);
    r.Export('%sstat.csv' % RebotConfig.path);
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
