# bot config.
# yunbi user config
import time;
class RebotConfig():
    # access key
    access_key = "e4986d53-5ea3cb58-f96bc6c8-3e02c";
    # secret key
    secret_key = "f11eee28-537fc560-53f4dd12-07941";

    # mysql config
    mysql_address = "localhost";
    mysql_user = "randy";
    mysql_password = "randy521";
    mysql_database = "bot";
    #data
    data_need_load = True;
    # user
    user_asset_ratio = 5;
    user_asset_least = 250;
    user_initamount = 2490;
    user_least_vol = 0.00001;
    # exchange
    exchange = 'tushare';#'chbtc';
    base_currency = 'cny';
    # rebot
    rebot_period = 240; # min
    rebot_buy_least_angle = 5;
    rebot_trade_sure_times = 1;
    rebot_do_per_period = 120;
    rebot_release = False;
    rebot_is_test = True;
    rebot_test_k_count = 1000;
    rebot_test_begin = time.time() - rebot_test_k_count / (24 * 60 / rebot_period) * 24*60*60; #1502006400;

    rebot_loss_ratio = -5;
    rebot_profit_ratio = -8;
    # rebot_trade_markets = [{'id':'etcusdt'}, {'id':'btcusdt'}, {'id':'bchusdt'},{'id':'ethusdt'},{'id':'ltcusdt'},{'id':'eosusdt'},{'id':'xrpusdt'},{'id':'omgusdt'},{'id':'dashusdt'},{'id':'zecusdt'},{'id':'htusdt'}];
    rebot_trade_markets = [];#[{'id':'300073'}];#[{'id':'603998'}, {'id':'603997'}]; #[{'id':'btccny'}, {'id':'ltccny'}, {'id':'ethcny'}, {'id':'etccny'}, {'id':'btscny'}]#[{'id':'luncny'}];
    # rebot_trade_markets = [{'id':'bchusdt'}];
    # file
    path = ''
    log = 'log.txt';
