from astropy.io import fits
import numpy as np
import tifffile as tiff
import time
import multiprocessing
import os
start = time.process_time()

#variables
bitn = 16
bitIn = 16

boolAll = 1

picNames = ["rgb", "r", "g", "b", "g1", "g2"]


m = 0.015

n = 8

manager = multiprocessing.Manager()
list1 = manager.list()
print(list1)
output = []
image_position = "fits/first_fit.fit"

lowPercentClip = 0
highPercentClip = 100

for i in range(n):
    list1.append(0)


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



#RGB Transform and Stretch OUTPUT ALL
#[0] = coloured [1] = red [2] = greenAVG [3] = blue [4] = green1 [5] = green2
def TransformStretchALL(resx, resy, data, bitIn, m, low, high, y, n):
    global list1
    start = int(((resy/(2*(n)))*y))
    stop = int((resy/(2*(n)))*(y+1))
    #print(start, stop)
    print("Process: " + str(y))
    output = [[],[],[],[],[],[]]
    fact = 1
    for i in range(start, stop):
    #for i in range(int(resy / 2)):
        xes = [[],[],[],[],[],[]]
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
            r = mappingFunction(preR*fact, m)*(2**bitn)
            g = mappingFunction(preG*fact, m)*(2**bitn)
            b = mappingFunction(preB*fact, m)*(2**bitn)
            
            
            
            xes[0].append((r, g, b))
            xes[1].append((r, 0, 0))
            xes[2].append((0, g, 0))
            xes[3].append((0, 0, b))
            xes[4].append((0, g, 0))
            xes[5].append((0, g, 0))
            
        if (i % 100) == 0:
            print(i)
        for i in range(len(output)):    
            output[i].append(xes[i])
    list1[y] = output
    print(list1[y])
    return
    
def TransformStretch(resx, resy, data, bitIn, m, low, high, y, n, q):
    start = int(((resy/(2*(n)))*y))
    stop = int((resy/(2*(n)))*(y+1))
    #print(start, stop)
    print("Process: " + str(y))
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
            r = mappingFunction(preR*fact, m)*(2**bitn)
            g = mappingFunction(preG*fact, m)*(2**bitn)
            b = mappingFunction(preB*fact, m)*(2**bitn)
            
            xes.append((r, g, b))
            
        if (i % 100) == 0:
            print(i)
            
        output.append(xes)
    list1[y] = output
    return

def multiProcessing(n, boolAll, resx, resy, data, bitIn, m, lowerClip, higherClip):
    global list1
    q = multiprocessing.Queue()
    Processes = []
    for i in range(n):
        #list1.append(0)
        Processes.append(0)
    final = []
    prefinal1 = []
    prefinal2 = []
    if boolAll == 0:
        for i in range(n):
            Processes[i] = multiprocessing.Process(target=TransformStretch, args=(resx, resy, data, bitIn, m,
                                                                                    lowerClip, higherClip, i, n, q,))
            print(Processes[i])
            Processes[i].start()
            #Processes = nP
    else:
        for i in range(n):
            Processes[i] = multiprocessing.Process(target=TransformStretchALL, args=(resx, resy, data, bitIn, m,
                                                                                       lowerClip, higherClip, i, n,))
            print(Processes[i])
            Processes[i].start()
    
    """if boolAll == 0:
        for i in range(n):
            queue = None
            queue = q.get()
            prefinal1.append(queue)"""
    """else:
        for i in range(n):
            queue = None
            print(type(q.get()))
            prefinal2.extend(queue)"""
    
    for i in range(n):
        Processes[i].join()
        print("Process joined: " + str(i))
        Processes[i].terminate()
        
    if boolAll == 0:
        final = []
        for i in range(n):
            final.extend(prefinal1[i])
        
    else:
        print(list1)
        final = [[],[],[],[],[],[]]
        for i in range(len(list1)):
            for j in range(len(list1[i])):
                final[j].extend(list1[i][j])
    return final


needed_data()

lowerClip = np.percentile(data, lowPercentClip)
higherClip = np.percentile(data, highPercentClip)
print(lowerClip, higherClip)

#output = TransformStretch(resx, resy, data, bitIn, m, lowerClip, higherClip, 0, 4)
if __name__ == '__main__':
    output = multiProcessing(n, boolAll, resx, resy, data, bitIn, m, lowerClip, higherClip)



if boolAll == 0:
    outArray = np.array(output, "uint" + str(bitn))
else:
    outArray = [[],[],[],[],[],[]]
    for i in range(len(output)):
        outArray[i] = np.array(output[i], "uint" + str(bitn))

#print(outArray)
print(time.process_time() - start)
start = time.process_time()

if boolAll == 0:
    tiff.imwrite(str(lowPercentClip) + "_" + str(highPercentClip) + "_m" + str(m) + "_" + str(bitn) + "bit_" + 'finite.tif', outArray, photometric='rgb')
    
else:
    directory = "ALL" + str(lowPercentClip) + "_" + str(highPercentClip) + "_m" + str(m) + "_" + str(bitn) + "bit_" + 'finite.tif'
    try:
        # Create target Directory
        os.mkdir(directory)
        print("Directory " , directory ,  " Created ") 
        for i in range(len(picNames)):
            tiff.imwrite("ALL" + str(lowPercentClip) + "_" + str(highPercentClip) + "_m" + str(m) + "_" + str(bitn) + "bit_" + 'finite.tif' + "/" + picNames[i] + "_" + str(lowPercentClip) + "_" + str(highPercentClip) + "_m" + str(m) + "_" + str(bitn) + "bit_" + 'finite.tif', outArray[i], photometric = "rgb")
    except FileExistsError:
        print("Directory " , directory ,  " already exists")
print(time.process_time() - start)    
