# wave from point
# we can found a set of point
from formula.K import K;
import csv

SegmentMinCount = 3;

class Direction():
    UP = 1;
    FLAT = 2;
    DOWN = 3;
'''
self.t = data[0];
self.o = data[1];
self.h = data[2];
self.l = data[3];
self.c = data[4];
self.vol = data[5];
'''

def ToStringDir(dir):
    if dir == Direction.UP:
        return 'UP';
    if dir == Direction.FLAT:
        return 'FLAT';
    if dir == Direction.DOWN:
        return 'DOWN';

def CalDir(k0, k1, k2):
    if k0 == None or k1 == None or k2 == None:
        return Direction.FLAT;
    if k0.h < k1.h and k1.h < k2.h:
        return Direction.UP;
    if k0.l > k1.l and k1.l > k2.l:
        return Direction.DOWN;
    return Direction.FLAT;

class Segment():
    def __init__(self, predir=Direction.FLAT):
        self.hkidx = -1;
        self.lkidx = -1;
        self.dir = Direction.FLAT;
        self.predir = predir;
        self.ks = [];

    def TimeInterval(self):
        i = self.hkidx - self.lkidx;
        return i > 0 and i or -i;
    def Amplitude(self):
        if self.dir == Direction.UP:
            return (self.hk.h - self.lk.l) / self.lk.l;
        if self.dir == Direction.DOWN:
            return (self.hk.h - self.lk.l) / self.hk.h;
    def Angle(self):# not a real angle
        if self.dir == Direction.UP:
            return (self.hk.h - self.lk.l) / (self.hkidx - self.lkidx);
        if self.dir == Direction.DOWN:
            return (self.lk.l - self.hk.h) / (self.lkidx - self.hkidx);
    def InputOneK(self, idx, k):
        if self.hkidx == -1:
            self.hk = k;
            self.hkidx = idx;
            self.lk = k;
            self.lkidx = idx;
            self.k0 = k;
            self.k1 = k;
            self.k2 = k;

        # k contain
        isContain = self.k2.Contain(k)
        if isContain:
            if self.dir == Direction.UP:
                self.k2 = K([k.t, 0, self.k2.h, k.l, 0, self.k2.vol + k.vol]);
            if self.dir == Direction.DOWN:
                self.k2 = K([k.t, 0, k.h, self.k2.l, 0, 0]);
        else:
            nk = None;
            if self.k2.h <= k.h :
                nk = K([k.t, 0, k.h, max(k.l, self.k2.l), 0, 0]);
            if self.k2.l >= k.l :
                nk = K([k.t, 0, min(k.h, self.k2.h), k.l, 0, 0]);
            self.k0 = self.k1; self.k1 = self.k2; self.k2 = nk;
            self.ks.append(nk);

        ndir = CalDir(self.k0, self.k1, self.k2);
        # print idx, isContain, self.dir, ndir;
        if isContain:
            return True, -1;
        if self.dir == Direction.FLAT:
            self.dir = ndir;
            if ndir == self.predir:
                if ndir == Direction.UP:
                    self.hkidx = idx; self.hk = k;
                if ndir == Direction.DOWN:
                    self.lkidx = idx; self.lk = k;
        if self.dir != ndir and ndir != Direction.FLAT: # break
            if self.dir == Direction.UP:
                return False, self.hkidx;
            if self.dir == Direction.DOWN:
                return False, self.lkidx;
        if ndir != Direction.FLAT or self.dir == Direction.FLAT:
            if self.lk.l > k.l:
                self.lkidx = idx; self.lk = k;
            if self.hk.h < k.h:
                self.hkidx = idx; self.hk = k;
        return True, -1;

    def __str__(self):
        return 'dir:{0}, hk.h:{1}, hk.h idx:{2}, lk.l:{3}, lk.l idx:{4}'.format(ToStringDir(self.dir), self.hk.h, self.hkidx, self.lk.l, self.lkidx);


class WaveKline():
    def __init__(self):
        self.data = [];
        self.segs = [];
        self.segs.append(Segment());
        self.idx = 0;

    def Input(self, klines):
        lk = len(klines);
        ps = self.segs[-1];
        for idx in range(self.idx, lk):
            rt, index = ps.InputOneK(idx, klines[idx])
            if rt == False :
                ps = Segment(ps.dir);
                # print 'insert new segment', len(self.segs) + 1;
                for k in range(index, idx+1):
                    ps.InputOneK(k, klines[k]);
                self.segs.append(ps);
        self.idx = lk;
    def Get(self, idx, dir=None):
        if dir == None:
            return self.segs[idx];
        else:
            l = len(self.segs);
            c = 0;
            if idx > 0:
                for i in range(0, l):
                    seg = self.segs[i];
                    if seg.dir == dir:
                        c = c + 1;
                    if c == idx + 1:
                        return seg;
            else:
                for i in range(0, l):
                    seg = self.segs[-i-1];
                    if seg.dir == dir:
                        c = c + 1;
                    if -c == idx:
                        return seg;
        return None;


    def Export(self, path):
        f = open(path, 'wb');
        w = csv.writer(f);
        l = len(self.segs);
        for k, v in enumerate(self.segs):
            if v.dir == Direction.UP:
                w.writerow([k, v.lk.h, v.lk.l, v.hk.h, v.hk.l]);
            else:
                w.writerow([k, v.hk.h, v.hk.l, v.lk.h, v.lk.l]);
            if k == l - 1:
                if v.dir == Direction.UP:
                    w.writerow([k, v.hk.h, v.hk.l, v.lk.h, v.lk.l]);
                else:
                    w.writerow([k, v.lk.h, v.lk.l, v.hk.h, v.hk.l]);
        f.close();

    def TrendWeaken(self):
        c = self.Get(-1);
        pc = self.Get(-2, c.dir);
        # 1/3 least
        if c.TimeInterval() * c.Amplitude() < pc.TimeInterval() * pc.Amplitude():
            return True;
        return False;
    def __str__(self):
        str = '';
        for k, seg in enumerate(self.segs):
           str += 'idx:{0}, '.format(k) + seg.__str__() + '\n';
        return str;

    def __getitem__(self, k):
        return self.segs[k];


