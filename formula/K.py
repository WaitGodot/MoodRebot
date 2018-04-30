#K
#
# o
# h
# l
# c
# vol
# increase
# amplitude

def ct(t):
    if t > 1000000000000:
        return t/1000;
    return t;

class K():
    def __init__(self, data=None, idx=-1):
        if data:
            self.Set(data);
        else:
            self.Set([0,0,0,0,0,0]);
        self.idx = idx

    def Set(self, data):
        self.t = ct(data[0]);
        self.o = data[1];
        self.h = data[2];
        self.l = data[3];
        self.c = data[4];
        self.vol = data[5];

        self.rmbvolume = self.vol * (self.h + self.l) / 2;
        self.increase = 0;
        if self.o > 0:
            self.increase = (self.c - self.o) / self.o;
        self.amplitude = 0;
        if self.l > 0:
            self.amplitude = (self.h - self.l) / self.l;

    def Contain(self, ohterk):
        if self.h >= ohterk.h and self.l <= ohterk.l :
            return True;
        return False;

    def __getitem__(self, k):
        if k == 't':
            return self.t;
        if k == 'o':
            return self.o;
        if k == 'h':
            return self.h;
        if k == 'l':
            return self.l;
        if k == 'c':
            return self.c
        if k == 'vol':
            return self.vol;
        if k == 'increase':
            return self.increase;
        if k == 'amplitude':
            return self.amplitude;

    def __str__(self):
        return 't = {0}, o = {1}, h = {2}, l = {3}, c = {4}, vol = {5}, increase = {6}, amplitude = {7}'.format(self.t, self.o, self.h, self.l, self.c, self.vol, self.increase, self.amplitude);

class KLine():
    def __init__(self):
        self.data = [];
        self.prices = []; # use close price
        self.volumes = []; # volume
        self.rmbvolumes = [];
        self.idx = 0;

    def Input(self, data):
        last = None;
        lend = len(self.data);
        if lend > 0:
            last = self.data[-1];
        for k, d in enumerate(data):
            if last:
                nt = ct(d[0]);
                if nt < last.t:
                    continue;
                if nt == last.t: # update close
                    last.Set(d);
                    self.prices[-1]     = last.c;
                    self.volumes[-1]    = last.vol;
                    self.rmbvolumes[-1] = last.rmbvolume;
                    continue;
            nk = K(d, self.idx);
            self.data.append(nk)
            self.prices.append(nk.c);
            self.volumes.append(nk.vol);
            self.rmbvolumes.append(nk.rmbvolume);
            self.idx += 1;
        return self.idx;

    def ToList(self, key, N=None):
        ret = [];
        if N == None:
            for k, d in enumerate(self.data):
                ret.append(d[key]);
        else:
            for idx in range(1, N):
                if len(self.data) >= idx:
                    ret.append(self.data[-idx][key]);

        return ret;

    def Get(self, k):
        if len(self.data) > 0:
            return self.data[k];
        return None;

    def __len__(self):
        return len(self.data);

    def __getitem__(self, k):
        return self.Get(k);

    def __str__(self):
        str = '';
        for k, v in enumerate(self.data):
            str = str + v.__str__() + '\n';
        return str;