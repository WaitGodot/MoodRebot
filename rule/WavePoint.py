# wave for float data

from rule.WaveKline import Direction
from rule.WaveKline import ToStringDir
import csv

def CalDir(fd0, fd1, fd2):
    if fd0 < fd1 and fd1 < fd2:
    	return Direction.UP;
    if fd0 > fd1 and fd1 > fd2:
        return Direction.DOWN;
    return Direction.FLAT;

class Point():
    def __init__(self, idx, fd):
        self.idx = idx;
        self.value = fd;
    def __str__(self):
        return 'idx={0} value={1}'.format(self.idx, self.value);

class Segment():
    def __init__(self):
        self.ps = [];
        self.dir = Direction.FLAT;
        self.high = Point(-1, 0);
        self.low = Point(-1, 0);
        self.start = Point(-1, 0);
        self.end = Point(-1, 0);
    def TimeInterval(self):
        i = self.high.idx - self.low.idx;
        return i > 0 and i or -i;
    def Amplitude(self):
        if self.dir == Direction.UP:
            return (self.high.value - self.low.value);
        if self.dir == Direction.DOWN:
            return (self.high.value - self.low.value);
    def Angle(self):# not a real angle
        if self.dir == Direction.UP:
            return (self.high - self.low) / (self.high.idx - self.low.idx);
        if self.dir == Direction.DOWN:
            return (self.low - self.high) / (self.low.idx - self.high.idx);
    def InputOneFloat(self, idx, fd):
        if self.high.idx == -1:
            self.high = Point(idx, fd);
            self.low = self.high;
            self.fd0 = fd;
            self.fd1 = fd;
            self.fd2 = fd;

        ndir = CalDir(self.fd1, self.fd2, fd);
        isContain = False;
        # point contain
        if self.dir == Direction.UP:
            if fd < self.fd2 and fd > self.fd1:
                self.fd1 = fd; isContain = True;
            elif fd > self.fd2 and fd < self.fd1:
                self.fd2 = fd; isContain = True;
            else:
                self.fd0 = self.fd1; self.fd1 = self.fd2; self.fd2 = fd;
        elif self.dir == Direction.DOWN:
            if fd > self.fd2 and fd < self.fd1:
                self.fd1 = fd; isContain = True;
            elif fd < self.fd1 and fd > self.fd1:
                self.fd2 = fd; isContain = True;
            else:
                self.fd0 = self.fd1; self.fd1 = self.fd2; self.fd2 = fd;
        else:
            self.fd0 = self.fd1; self.fd1 = self.fd2; self.fd2 = fd;

        print idx, ToStringDir(ndir), ToStringDir(self.dir), isContain, fd;
        if self.dir == Direction.FLAT:
            self.dir = ndir;
        if isContain:
            return True, -1;
        if self.dir != ndir and ndir != Direction.FLAT: # break
            if self.dir == Direction.UP:
                return False, self.high.idx;
            if self.dir == Direction.DOWN:
                return False, self.low.idx;
        if ndir != Direction.FLAT or self.dir == Direction.FLAT:
            if self.high.value < fd:
                self.high = Point(idx, fd);
            if self.low.value > fd:
                self.low = Point(idx, fd);
        return True, -1;

    def InputOneFloatTrend(self, idx, fd):
        if self.start.idx == -1:
            self.start = Point(idx, fd);
            self.end = self.start;
            self.fd0 = fd;
            self.fd1 = fd;
            self.fd2 = fd;

        # point contain
        ndir = CalDir(self.fd1, self.fd2, fd);
        isContain = False;
        if self.dir == Direction.UP:
            if fd < self.fd2 and fd > self.fd1:
                self.fd1 = fd; isContain = True;
            elif fd > self.fd2 and fd < self.fd1:
                self.fd2 = fd; isContain = True;
            else:
                self.fd0 = self.fd1; self.fd1 = self.fd2; self.fd2 = fd;
        elif self.dir == Direction.DOWN:
            if fd > self.fd2 and fd < self.fd1:
                self.fd1 = fd; isContain = True;
            elif fd < self.fd1 and fd > self.fd1:
                self.fd2 = fd; isContain = True;
            else:
                self.fd0 = self.fd1; self.fd1 = self.fd2; self.fd2 = fd;
        else:
            self.fd0 = self.fd1; self.fd1 = self.fd2; self.fd2 = fd;

        #print idx, ToStringDir(ndir), ToStringDir(self.dir), isContain, fd;
        self.end = Point(idx-2, self.fd0);
        if self.dir == Direction.FLAT:
            self.dir = ndir;
        if isContain:
            return True, -1;
        if self.dir != ndir and ndir != Direction.FLAT: # break
            return False, self.end.idx
        return True, -1;

    def __str__(self):
        return 'dir:{0}, high:{1}, low:{2}, start:{3}, end:{4}'.format(ToStringDir(self.dir), self.high.__str__(), self.low.__str__(), self.start, self.end);

class WavePoint():
    def __init__(self):
        self.segs = [];
        self.segs.append(Segment());
        self.points = [];
        self.idx = 0;

    def Input(self, fds):
        lk = len(fds);
        ps = self.segs[-1];
        for idx in range(self.idx, lk):
            # print 'input', idx, lk, fds[idx];
            if fds[idx] == 1990214:
                continue;
            rt, index = ps.InputOneFloat(idx, fds[idx])
            if rt == False :
                print 'insert new segment', ps, index
                ps = Segment();
                for k in range(index, idx+1):
                    if fds[idx] == 1990214:
                        continue;
                    ps.InputOneFloat(k, fds[k]);
                self.segs.append(ps);
        self.idx = lk;

    def InputTrend(self, fds):
        lk = len(fds);
        ps = self.segs[-1];
        for idx in range(self.idx, lk):
            # print 'input', idx, lk, fds[idx];
            if fds[idx] == 1990214:
                continue;
            rt, index = ps.InputOneFloatTrend(idx, fds[idx])
            if rt == False :
                # print 'insert new segment', ps, index
                ps = Segment();
                for k in range(index, idx+1):
                    if fds[idx] == 1990214:
                        continue;
                    ps.InputOneFloatTrend(k, fds[k]);
                self.segs.append(ps);
        self.idx = lk;
        lseg = len(self.segs);
        lpoint = len(self.points);
        if lseg > lpoint + 1:
            for k in range(lpoint, lseg-1):
                if k == 0:
                    self.points.append(self.segs[1].end.value);
                self.points.append(self.segs[k+1].end.value);

    def Export(self, path):
        f = open(path, 'wb');
        w = csv.writer(f);
        l = len(self.segs);
        for k, v in enumerate(self.segs):
            if v.dir == Direction.UP:
                w.writerow([k, v.low.value]);
            else:
                w.writerow([k, v.high.value]);
            if k == l - 1:
                if v.dir == Direction.UP:
                    w.writerow([k, v.high.value]);
                else:
                    w.writerow([k, v.low.value]);
        f.close();

    def ExportTrend(self, ks, path):
        f = open(path, 'wb');
        w = csv.writer(f);
        l = len(self.segs);
        for k, v in enumerate(self.segs):
            if k == 1:
                w.writerow([ks[v.start.idx].t, v.start.value]);
            w.writerow([ks[v.start.idx].t, v.end.value]);
        f.close();

    def ToPoints(self):
        l = len(self.segs);
        rt = []
        for k, v in enumerate(self.segs):
            if v.dir == Direction.UP:
                rt.append(v.low);
            else:
                rt.append(v.high);
            if k == l - 1:
                if v.dir == Direction.UP:
                    rt.append(v.high);
                else:
                    rt.append(v.low);

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

    def TrendWeaken(self, dir):
        c = self.Get(-1, dir);
        pc = self.Get(-2, dir);
        if pc == None:
            return False;
        # 1/3 least
        if c.TimeInterval()*c.Amplitude() < pc.TimeInterval()*pc.Amplitude():
            return True;
        return False;

    def __str__(self):
        str = '';
        for k, seg in enumerate(self.segs):
           str = str + seg.__str__() + '\n';
        return str;

    def __getitem__(self, k):
        return self.segs[k];
