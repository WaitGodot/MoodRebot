'''
RSV:=(CLOSE-LLV(LOW,N))/(HHV(HIGH,N)-LLV(LOW,N))*100;
K:SMA(RSV,M1,1);
D:SMA(K,M2,1);
J:3*K-2*D;
'''
from formula.Formula import *
import csv

class DATA():
    def __init__(self, k, d, j):
        self.k = k;
        self.d = d;
        self.j = j;
    def __str__(self):
        return 'k={0},d={1},j={2}'.format(self.k, self.d, self.j);

class KDJ():
    def __init__(self, N1=9, N2=3, N3=3):
        self.N1 = N1;
        self.N2 = N2;
        self.N3 = N3;
        self.hightArr = [];
        self.lowArr = [];
        self.RSV = [];
        self.K = [];
        self.D = [];
        self.J = [];
        self.preK2D = None;
        self.curK2D = None;
        self.preD2K = None;
        self.curD2K = None;

    def Input(self, klines):
        l = len(self.hightArr);
        prices = klines.prices;

        HIGH(klines.ToList('h'), self.hightArr, self.N1);
        LOW(klines.ToList('l'), self.lowArr, self.N1);
        
        for idx in range(l, len(prices)):
            rsv = (prices[idx] - self.lowArr[idx]) / (self.hightArr[idx] - self.lowArr[idx]) * 100;
            self.RSV.append(rsv);
       
        l = len(self.K);
        for idx in range(l, len(self.RSV)):
            SMA(self.RSV, self.K, self.N2, 1);

        l = len(self.D);
        for idx in range(l, len(self.K)):
            SMA(self.K, self.D, self.N3, 1)
       
        l = len(self.J);
        for idx in range(l, len(self.K)):
            self.J.append(self.K[idx] * 3 - self.D[idx] * 2);

    def Get(self, idx):
        return DATA(self.K[idx], self.D[idx], self.J[idx]);

    def Do(self):
        k2d = CROSS(self.K, self.D);
        if k2d:
            idx = len(self.K);
            self.preK2D = self.curK2D;
            self.curK2D = [idx, (self.K[-1] + self.D[-1])/2];
            if self.preK2D and self.curK2D[1] < 80 and self.curK2D[1] >= 20 and self.curK2D[0] - self.preK2D[0] >= 5:
                return 'buy'
        d2k = CROSS(self.D, self.K);
        if d2k:
            idx = len(self.K);
            self.preD2K = self.curD2K;
            self.curD2K = [idx, (self.K[-1] + self.D[-1])/2];
            if self.preD2K and self.curD2K[1] / self.preD2K[1] <= 0.88 and self.curD2K[0] - self.preD2K[0] >= 5:
                return 'sell'
        return None;

    def Export(self, path):
        f = open(path, 'wb');
        w = csv.writer(f);
        w.writerow(['id', 'k', 'd', 'j']);
        for k in range(len(self.K)):
            w.writerow([k, self.K[k], self.D[k],  self.J[k],]);

        f.close();

    def __str__(self):
        str = '';
        l = len(self.K);
        for k in range(0, l):
            str = str + self.Get(indx).__str__() + '\n';
        return str;
    def __len__(self):
        return len(self.K);
