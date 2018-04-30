import time
import urllib2
import math
from exchange.Exchange import Exchange
from exchange.yunbiEX import yunbiEX
from exchange.yunbiEX import yunbiEXLocal
from exchange.chbtcEX import chbtcEX
from exchange.chbtcEX import chbtcEXLocal
from exchange.tushareEX import tushareEXLocal
from exchange.huobiEX import huobiEX
from exchange.huobiEX import huobiEXLocal

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
from rule.WVStats import WVStats
from user.User import User
from Time import Time
from Log import Log

class Rebot():
    def __init__(self, period):
        self.period = period;
        self.exchange = Exchange(RebotConfig.access_key, RebotConfig.secret_key);
        delegate = None;
        if RebotConfig.exchange == 'chbtc':
            if RebotConfig.rebot_release:
                delegate = chbtcEX();
            else:
                delegate = chbtcEXLocal();
        if RebotConfig.exchange == 'yunbi':
            if RebotConfig.rebot_release:
                delegate = yunbiEX();
            else:
                delegate = yunbiEXLocal();
        if RebotConfig.exchange == "tushare":
            delegate = tushareEXLocal();
        if RebotConfig.exchange == "huobi":
            if RebotConfig.rebot_release:
                delegate = huobiEX();
            else:
                delegate = huobiEXLocal();

        self.exchange.delegate(delegate);
        # time
        Time.SetServerTime(self.exchange.getServerTimestamp())
        # data.
        if RebotConfig.data_need_load:
            self.exchange.loadData(period, RebotConfig.rebot_test_begin);
        self.exchange.prepare(period, RebotConfig.rebot_test_begin);
        # user.
        self.user = User();
        info = self.exchange.getUser();
        print info
        print '-----------------------------------'
        self.user.updatePositions(info['accounts']);
        # markets
        self.markets = self.exchange.getMarkets();
        # rule.
        self.rules = {};
        # init.
        #
        for k,v in enumerate(self.markets):
            market = v['id'];
            # order.
            # done in right env.
            self.user.updateOrder(self.exchange.getOrder(market));
            # k line.
            if RebotConfig.rebot_is_test:
                dk = self.exchange.getK(market, 42, self.period, RebotConfig.rebot_test_begin); # 1498838400:2017/7/1 0:0:0; 1496246400:2017/6/1 0:0:0; 1493568000:2017/5/1 0:0:0
            else:
                dk = self.exchange.getK(market, 500, self.period);

            r = WVStats();
            # r = MutliMovingAverage();
            r.Run(dk);
            lastk=r.KLines.Get(-1);
            if lastk:
                currency = market;#market[0:len(market)-3];
                self.user.updateHigh(currency, lastk.c); # c or high
                self.user.updateCost(currency, lastk.c)

            self.rules[market] = r;
            Log.d('index:%d, start market:%s, begin time %s, current time:%s'%(k, market, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(r.KLines.Get(0).t)), time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(lastk.t))));
        #scale.
        self.scales = [];

    def run(self):
        # print '-----------------------------------------------------------------'
        # markets
        nmarkets = self.exchange.getMarkets()
        if nmarkets:
            self.markets = nmarkets;
        # user
        info = self.exchange.getUser();
        self.user.updatePositions(info['accounts']);
        if RebotConfig.rebot_release:
            print 'positions:';
            for k,v in (self.user.positions.items()):
                if v['volume'] > 0:
                    print '\t{0} {1}'.format(k, v);
            # print '\n'

        sv  = self.user.positions[RebotConfig.base_currency]['volume'];
        flag=False;
        stop=True;
        buylist     = [];
        selllist    = [];
        for k,v in enumerate(self.markets):
            market = v['id'];
            # order.
            # done in right env.
            orders = self.user.updateOrder(self.exchange.getOrder(market));
            # rule
            r = self.rules[market];
            lastk=r.KLines.Get(-1);
            prelastk=lastk;
            # k line.
            # dk = self.exchange.getK(market, 500, self.period, lastk.t);
            # print 'do market : %s' % market;
            dk=None;
            if lastk:
                kcount = int(math.floor((time.time()-lastk.t)/(self.period*60)) + 2);
                if kcount < 2:
                    kcount = 2;
                dk = self.exchange.getK(market, kcount, self.period, lastk.t);
            #    print dk
            type = None;
            if dk and len(dk) > 0:
                ret     = r.Run(dk);
                lastk   = r.KLines.Get(-1);
                if RebotConfig.rebot_release:
                    print market, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(lastk.t)), time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), lastk
                type    = ret.get('type');

            for orderkey, o in enumerate(orders):
                if o.checkMustCancel():
                    Log.d('\tcancel olded order {0}'.format(o));
                    self.exchange.doOrderCancel(o.id, market);

            #print '\tmarket status : {1}, last k time : {2}, type : {3}'.format(market, r.status, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(lastk.t)), type);
            if lastk and prelastk and lastk.t != prelastk.t:
                stop = False;
            currency = market[0:len(market) - len(RebotConfig.base_currency)];
            pc = self.user.positions.get(currency);

            scaleless = False;
            if pc and lastk:
                current = pc['volume'] * lastk.c;
                sv += current;
                self.user.updateHigh(currency, lastk.c); # c or high
                cost = self.user.getCost(currency);

                if cost and cost > 0 and False:
                    scale = (current - cost)/cost*100;
                    rate = RebotConfig.rebot_loss_ratio;
                    if scale < rate:
                        if RebotConfig.rebot_is_test:
                            prate = (1 + rate * 1.1 / 100);
                            nprateprice = pc['price'] * prate;
                            vol = self.user.doOrder(market, 'sell', nprateprice);
                            print '\tmarket:%s, do sell, price:%f scale less %f, volume:%f, price:%f, time:%s' % (market, pc['price'], rate, vol, nprateprice, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(lastk.t)));
                            scaleless = True;
                            self.exchange.doOrder(market, 'sell', nprateprice, vol, lastk.t);
                    # else:
                    #    print '\tmarket:{0}, scale:{1}, position high price:{2}, current price{3}'.format(market, scale, pc['high'], lastk.c);
                cost = self.user.getHighCost(currency);
                if cost and cost > 0 and scaleless == False and False:
                    scale = (current - cost)/cost*100;
                    rate = RebotConfig.rebot_profit_ratio;
                    if scale < rate:
                        if RebotConfig.rebot_is_test:
                            prate = (1 + rate * 1.1 / 100);
                            nprateprice = pc['high'] * prate;
                            vol = self.user.doOrder(market, 'sell', nprateprice);
                            print '\tmarket:%s, do sell, high:%f scale less %f, volume:%f, high:%f, time:%s' % (market, pc['high'], rate, vol, nprateprice, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(lastk.t)));
                            scaleless = True;
                            self.exchange.doOrder(market, 'sell', nprateprice, vol, lastk.t);
                    # else:
                    # print '\tmarket:{0}, scale:{1}, position high price:{2}, current price{3}'.format(market, scale, pc['high'], lastk.c);
                #if scaleless == False:
                #    selllist.append({'market':market, 'result':{'k':lastk, 'ext':'rebot profit ratio' }})

            if scaleless == False:
                if type == 'buy':
                    buylist.append({'market':market, 'result':ret})
                if type == 'sell':
                    selllist.append({'market':market, 'result':ret})

        # print 'do orders:'
        # sell
        nselllist = [];
        for key,v in enumerate(selllist):
            market  = v['market'];
            nselllist.append(v);
        for key,v in enumerate(nselllist):
            market  = v['market'];
            k   = v['result']['k'];
            vol = self.user.doOrder(market, 'sell', k.c);
            if vol and vol > 0:
                flag = True;
                orderresult, price, vol = self.exchange.doOrder(market, 'sell', k.c, vol, k.t);
                r = self.rules[market];
                r.OrderResult(v['result'], orderresult);
                Log.d('\tmarket:{0}, do:{1}, result:{2}, price:{3}, volume:{4}, time:{5}, ext:{6}'.format(market, 'SELL', orderresult, price, vol, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(k.t)), v['result']['ext']));
            #else:
            #    print '\tmarket:%s, not enough to sell' % market;

        # buy
        nbuylist = [];
        for key,v in enumerate(buylist):
            market = v['market'];
            sort = v['result']['sort'];
            v['sort'] = sort
            angle = v['result'].get('angle');
            k   = v['result']['k'];

            # print '\tmarket %s sort %f, angle %f, time %s' % (market, sort, angle, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(k.t)));
            if sort > 100 or sort < 0:
                print '\tmarket %s sort illegal, sort %f, time %s' % (market, sort, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(k.t)));
                continue;
            if angle and angle < RebotConfig.rebot_buy_least_angle:
                print '\tmarket %s angle illegal, angle %f, time %s' % (market, angle, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(k.t)));
                continue;
            nbuylist.append(v);
            # nbuylist.append(v);

        nbuylist.sort(key=lambda v: v['sort'], reverse=False)
        for key,v in enumerate(nbuylist):
            market  = v['market'];
            k   = v['result']['k'];
            vol = self.user.doOrder(market, 'buy', k.c);
            if vol and vol > 0:
                flag=True;
                orderresult, price, vol = self.exchange.doOrder(market, 'buy', k.c, vol, k.t, {'sort':v['sort']});
                Log.d('\tmarket:{0}, do:{1}, result:{2}, price:{3}, volume:{4}, time:{5}, ext:{6}'.format(market, 'BUY', orderresult, price, vol, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(k.t)), v['result']['ext']));
            else:
                print '\tnot enough cny !!! market:{0}, do:{1}, price:{2}, volume:{3}, time:{4}'.format(market, 'buy', k.c, vol, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(k.t)));
            #else:
            #    print '\t!!! market:{0}, time:{1}, buy fail less volume : {2}'.format(market, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(cwave.ck.t)), v['rmbvolumeN3']);
        if flag:
            ascale = (sv - self.user.initamount)/self.user.initamount*100;
            self.scales.append(ascale);
            Log.d('all scale:{0}, current cny:{1}\n'.format(ascale, sv));
        return stop;


