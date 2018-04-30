
# database;
import MySQLdb
import sys
import time
import datetime

from RebotConfig import RebotConfig;
DATA=['k'];

class Database():
    def __init__(self):
        db = MySQLdb.connect(RebotConfig.mysql_address, RebotConfig.mysql_user, RebotConfig.mysql_password);
        if db :
            self.cursor = db.cursor();
            self.cursor.execute("use {0}".format(RebotConfig.mysql_database));
            self.db = db;
            self.data = {};

            self.cursor.execute("select * from markets");
            markets = self.cursor.fetchall();
            for k, market in enumerate (markets) : # id name opentime
                md = {};
                name = market[1];
                for i,d in enumerate(DATA):
                    self.cursor.execute("select * from {0}_{1}".format(name, d));
                    nd = self.cursor.fetchall();
                    if nd :
                        md[d] = nd;
                    else:
                    	md[d] = [];

                self.data[name] = md;
        else:
            print "can not connect the mysql, please check 'RebotConfig'";
            sys.exit(1);


    def Get(self, market, ele):
        md = self.data[market];
        if md :
            return md[ele];
        else :
            print "not found market {0}".format(market);
        return None;
    
    def Add(self, market, ele, period, data):
        md = self.data[market];
        if md == None :
            print "not found market {0}".format(market);
            return False;
        mde = md[ele];
        print market, ele, mde
        if mde == None:
            print "market {0} not found element {1}".format(market, ele);
            return False;
        mde.extend(data);
        return True;

    def Save(self):
        for name,md in self.data.items():
            # k
            dk = md['k'];
            for k, d in enumerate(dk):
                # timestamp = datetime.datetime.fromtimestamp(d.t).strftime('%Y-%m-%d %H:%M:%S')
                self.cursor.execute('''insert into {0}_k 
            	   	(time,o,h,l,c,vol,increase,amplitude) values
            		({1},{2},{3},{4},{5},{6},{7},{8})'''.format(name, d.t, d.o, d.h, d.l, d.c, d.vol, d.increase, d.amplitude));

            # macd
            '''
            dmacd = md['macd'];
            for k, d in enumerate(dmacd):
                self.cursor.execute('''insert into {0}_macd
            		(time, diff, dea, macd) values
            		({1}, {2}, {3}, {4})'''.format(name, d.time, d.diff, d.dea, d.macd));
            '''
        self.db.commit();

    def Close(self):
        self.Save();
        self.cursor.close();
        self.db.close();


