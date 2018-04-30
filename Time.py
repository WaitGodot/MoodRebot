# time

import time

class Time():
    servertime = 0;
    localtime = 0;
    @staticmethod
    def SetServerTime(t):
        Time.servertime = t;
        Time.localtime = time.time();
    @staticmethod
    def Time():
    	if Time.servertime == 0:
    		return time.time();
        return time.time() - Time.localtime + Time.servertime;