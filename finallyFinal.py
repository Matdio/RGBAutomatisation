from astropy.io import fits
import numpy as np
import tifffile as tiff
import time
import threading
start = time.process_time()

#variables
bitn = 16
bitIn = 16

m = 0.001

n = 8

output = []
image_position = "fits/first_fit.fit"

lowPercentClip = 70
highPercentClip = 100

tOutput = []


#check if resolution is divisible by 2 and is odd
def fix_res(res):
    while (res % 2) != 0:
        res = res - 1
    return(res)

#define hdul, get resolution, get data
def needed_data():
    global resx, resy, data
    hdul = fits.open(image_position)
    resx = fix_res(hdul[0].header[3])
    resy = fix_res(hdul[0].header[4])
    data = hdul[0].data

#function for mapping
def mappingFunction(x, m):
    if x == 0:
        return 0
    elif x == m:
        return 0.5
    elif x == 1:
        return 1
    else:
        return ((m-1)*x)/((((2*m)-1)*x)-m)
    #return x
    #return x**0.5

#RGB Transform and Stretch
def TransformStretch(resx, resy, data, bitIn, m, low, high, y, n):
    global tOutput
    start = int(((resy/(2*(n)))*y))
    stop = int((resy/(2*(n)))*(y+1))
    #print(start, stop)
    output = []
    fact = 1
    for i in range(start, stop):
    #for i in range(int(resy / 2)):
        xes = []
        for j in range(int(resx / 2)):
            preR = data[i*2-1][j*2-1]
            preG = (data[i*2][j*2-1] + data[i*2-1][j*2])/2
            preB = data[i*2][j*2]
            preR = (preR - low)/ (high - low)
            preG = (preG - low)/ (high - low)
            preB = (preB - low)/ (high - low)
            if preR <= 0:
                preR = 0
            if preR >= 1:
                preR = 1
            if preG <= 0:
                preG = 0
            if preG >= 1:
                preG = 1
            if preB <= 0:
                preB = 0
            if preB >= 1:
                preB = 1
            r = mappingFunction(preR*fact, m)*(2**bitIn)
            g = mappingFunction(preG*fact, m)*(2**bitIn)
            b = mappingFunction(preB*fact, m)*(2**bitIn)
            
            
            
            xes.append((r, g, b))
            
        if (i % 100) == 0:
            print(i)
            
        output.append(xes)
    tOutput[y] = output

def multiThreading(n):
    global resx, resy, data, bitIn, m, lowerClip, higherClip, tOutput
    Threads = []
    for i in range(n):
        nT = threading.Thread(target = TransformStretch, args = (resx, resy, data, bitIn, m, lowerClip, higherClip, i, n,))
        Threads.append(nT)
    output = []
    for i in range(n):
        tOutput.append(0) 
    for i in range(n):
        Threads[i].start()
        #print(output)
    for i in range(n):
        Threads[i].join()
    final = []
    for i in range(len(tOutput)):
        final.extend(tOutput[i])
    
    return final

needed_data()

lowerClip = np.percentile(data, lowPercentClip)
higherClip = np.percentile(data, highPercentClip)
#print(lowerClip, higherClip)

#output = TransformStretch(resx, resy, data, bitIn, m, lowerClip, higherClip, 0, 4)
output = multiThreading(n)
outArray = np.array(output, "uint16")

#print(outArray)
print(time.process_time() - start)

tiff.imwrite('finite.tif', outArray, photometric='rgb')