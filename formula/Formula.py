# formula

#MA
def MA(xArr, yArr, N):
    lenY = len(yArr);
    lenX = len(xArr);
    for idx in range(lenY, lenX):
        ss = 0;
        av = 0;
        for k in range(0, N):
            nidx = idx - k;
            if nidx < 0:
                av = ss / float(k);
                break;
            else:
                ss += xArr[nidx];
        if av == 0:
            yArr.append(ss / float(N));
        else:
            yArr.append(av);

#EMA
def EMA(xArr, yArr, N):
    k = (2.0 / (N + 1.0));
    lenY = len(yArr);
    lenX = len(xArr);
    for idx in range(lenY, lenX):
        value = xArr[idx];
        if idx != 0:
            yArr.append(value * k + (1.0 - k) * yArr[idx - 1]);
        else:
            yArr.append(value);

#SMA(X,N,M) = SMA(N-1) * (N-M)/N + X(N)*M/N
def SMA(xArr, yArr, N, M):
    lenX = len(xArr);
    lenY = len(yArr);
    for idx in range(lenY, lenX):
        value = xArr[idx];
        if idx != 0:
            yArr.append(value*(float)(M)/(float)(N) + yArr[idx - 1] * ((float)(N)-(float)(M))/(float)(N));
        else:
            yArr.append(value);
#HIGH
def HIGH(xArr, yArr, N):
    lenX = len(xArr);
    lenY = len(yArr);
    for idx in range(lenY, lenX):
        high = 0;
        for n in range(0, N):
            nidx = idx - n;
            if nidx < 0:
                break;
            value = xArr[nidx];
            if high == 0:
               high = value;
            if high < value:
               high = value;
        yArr.append(high);
#LOW
def LOW(xArr, yArr, N):
    lenX = len(xArr);
    lenY = len(yArr);
    for idx in range(lenY, lenX):
        low = 0;
        for n in range(0, N):
            nidx = idx - n;
            if nidx < 0:
                break;
            value = xArr[nidx];
            if low == 0:
               low = value;
            if low > value:
               low = value;
        yArr.append(low);

#CROSS
def CROSS(AArr, BArr, N=None):
    lena = len(AArr);
    lenb = len(BArr);
    if N == None:
        N = lena-1;
    if N < 0:
        N = lena + N;
    if lena < N or lenb < N or N < 2:
        return False;
    if AArr[N-1] <= BArr[N-1] and AArr[N] >= BArr[N]:
        return True;
    return False;

# MAX
def MAX(Arr, idx1=None, idx2=None):
    l = len(Arr);
    if l <= 0:
        return None;
    idx1 = 0 if idx1==None else idx1;
    idx2 = l if idx2==None else idx2;
    value = Arr[idx1];
    for idx in range(idx1, idx2):
        if Arr[idx] > value:
            value = Arr[idx];
    return value;

# MIN
def MIN(Arr, idx1=None, idx2=None):
    l = len(Arr);
    if l <= 0 or (idx2 > 0 and l <= idx2) or (idx1 < 0 and l + idx1 < 0):
        return None;
    idx1 = 0 if idx1==None else idx1;
    idx2 = l if idx2==None else idx2;
    value = Arr[idx1];
    for idx in range(idx1, idx2):
        if Arr[idx] < value:
            value = Arr[idx];
    return value;

# SUM
def SUM(Arr, idx1=None, idx2=None):
    l = len(Arr);
    if l <= 0 or (idx2 > 0 and l <= idx2) or (idx1 < 0 and l + idx1 < 0):
        return 1;
    idx1 = 0 if idx1==None else idx1;
    idx2 = l if idx2==None else idx2;
    value = 0;
    for idx in range(idx1, idx2):
        value += Arr[idx];
    if value < 1:
        return 1;
    return value;

# RATE
def RATE(xArr, yArr, idx=None):
    lenX = len(xArr);
    lenY = len(yArr);
    if idx == None:
        idx = 0;
    for k in range(lenY, lenX):
        if k > idx:
            yArr.append(xArr[k] - xArr[k-1]);
        else:
            yArr.append(1990214);

def ZERO( count):
    if count == 1:
        return '0';
    if count == 2:
        return '00';
    if count == 3:
        return '000';
    if count == 4:
        return '0000';
    if count == 5:
        return '00000';

def NORMALIZE(id):
    if len(id) < 6:
        id = '%s%s' % (ZERO(6 - len(id)), id);
    return id;
