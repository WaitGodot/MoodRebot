from formula.Formula import EMA

# MACD
class DATA():
    def __init__(self, diff, dea):
        self.Set(diff, dea)

    def Set(self, diff, dea):
        self.diff = diff;
        self.dea = dea;
        self.macd = 2 * (self.diff - self.dea);

    def __str__(self):
        return 'diff={0},dea={1},macd={2}'.format(self.diff, self.dea, self.macd);

class MACD():
    def __init__(self, short=12, long=26, diff=9):
        self.EMAShort = [];
        self.EMALong = [];
        self.DEA = [];
        self.DIFF = [];
        self.short = short;
        self.diff = diff;
        self.long = long;

    def Input(self, klines):
        prices = klines.prices;
        EMA(klines.prices, self.EMAShort, self.short);
        EMA(klines.prices, self.EMALong, self.long);

        ld = len(self.DIFF);
        lr = len(self.EMAShort);
        for idx in range(ld, lr):
            self.DIFF.append(self.EMAShort[idx] - self.EMALong[idx]);
        EMA(self.DIFF, self.DEA, self.diff);
    
    def Get(self, index):
        return DATA(self.DIFF[index], self.DEA[index])

    def __str__(self):
        str = '';
        l = len(self.EMAShort);
        for k in range(0, l):
            str = str + self.Get(indx).__str__() + '\n';
        return str;
    def __len__(self):
        return len(self.DIFF);