from astropy.io import fits
import numpy as np
import tifffile as tiff
import time
import os
from multiprocessing import Process, Queue
start = time.process_time()

#variables
bitn = 16
bitIn = 16

boolAll = 1

picNames = ["rgb", "r", "g", "b", "g1", "g2"]

name = "Picture1"


m = 0.015

n = 4

output = []
image_position = "fits/first_fit.fit"

lowPercentClip = 0
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



#RGB Transform and Stretch OUTPUT ALL
#[0] = coloured [1] = red [2] = greenAVG [3] = blue [4] = green1 [5] = green2
def TransformStretchALL(resx, resy, data, bitIn, m, low, high, y, n, queue):
    global tOutput
    start = int(((resy/(2*(n)))*y))
    stop = int((resy/(2*(n)))*(y+1))
    #print(start, stop)
    output = [[],[],[],[],[],[]]
    fact = 1
    for i in range(start, stop):
    #for i in range(int(resy / 2)):
        xes = [[],[],[],[],[],[]]
        for j in range(int(resx / 2)):
            preR = data[i*2][j*2]
            preG = (data[i*2][j*2+1] + data[i*2+1][j*2])/2
            preB = data[i*2+1][j*2+1]
            preR = (preR - low)/ (high - low)
            preG = (preG - low)/ (high - low)
            preB = (preB - low)/ (high - low)
            preG1 = data[i*2][j*2+1]
            preG2 = data[i*2+1][j*2]
            preG1 = (preG1 - low)/ (high - low)
            preG2 = (preG2 - low)/ (high - low)
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
            if preG1 <= 0:
                preG1 = 0
            if preG1 >= 1:
                preG1 = 1
            if preG2 <= 0:
                preG2 = 0
            if preG2 >= 1:
                preG2 = 1
            r = mappingFunction(preR*fact, m)*(2**bitn)
            g = mappingFunction(preG*fact, m)*(2**bitn)
            b = mappingFunction(preB*fact, m)*(2**bitn)
            #g1 = mappingFunction(preG1*fact, m)*(2**bitn)
            #g2 = mappingFunction(preG2*fact, m)*(2**bitn)
            g1 = g
            g2 = g
            
            
            
            xes[0].append((r, g, b))
            xes[1].append((r, 0, 0))
            xes[2].append((0, g, 0))
            xes[3].append((0, 0, b))
            xes[4].append((0, g1, 0))
            xes[5].append((0, g2, 0))
            
        if (i % 100) == 0:
            print(i)
        for i in range(len(output)):    
            output[i].append(xes[i])
    queue.put(output)
    
def TransformStretch(resx, resy, data, bitIn, m, low, high, y, n, queue):
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
            preR = data[i*2][j*2]
            preG = (data[i*2][j*2+1] + data[i*2+1][j*2])/2
            preB = data[i*2+1][j*2+1]
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
    queue.put(output)
    
    
def main(n):
    print(n)
    global tOutput
    queue = Queue()
    processes = []
    for i in range(n):
        processes.append([])
    
    if boolAll == 0:
        for _ in range(n):
            print("creating processes")
            processes[_] = Process(target=TransformStretch(resx, resy, data, bitIn, m, lowerClip, higherClip, _, n, queue))
            print("created processes")    
    else:
        for _ in range(n):
            print("creating processes")
            processes[_] = Process(target=TransformStretchALL(resx, resy, data, bitIn, m, lowerClip, higherClip, _, n, queue))
            print("created processes")      
    
    
    for p in processes:
        print("started:" + str(p))
        p.start()
    
    results = []
    counter = 0
    while counter < len(processes):
        temp = queue.get()
        if temp == None:
            continue
        else:
            results.append(temp)
            counter +=1
    
    for p in processes:
        print("waiting for:" + str(p))
        p.join()
        print("joined:" + str(p))
        
    tOutput = results

def combine(array):
    if boolAll == 0:
        final = []
        for i in range(len(array)):
            final.extend(array[i])
    else:
        final = [[],[],[],[],[],[]]
        for i in range(len(array)):
            for j in range(len(array[i])):
                final[j].extend(array[i][j])

needed_data()



lowerClip = np.percentile(data, lowPercentClip)
higherClip = np.percentile(data, highPercentClip)
print(lowerClip, higherClip)


y = 0

if __name__ == "__main__":
    main(n)

"""if boolAll == 0:
    TransformStretch(resx, resy, data, bitIn, m, lowerClip, higherClip, y, n)
else:
    TransformStretchALL(resx, resy, data, bitIn, m, lowerClip, higherClip, y, n)"""




    
output = combine(tOutput)



if boolAll == 0:
    outArray = np.array(output, "uint" + str(bitn))
else:
    outArray = [[],[],[],[],[],[]]
    for i in range(len(output)):
        print(i)
        outArray[i] = np.array(output[i], "uint" + str(bitn))

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
            tiff.imwrite("ALL" + str(lowPercentClip) + "_" + str(highPercentClip) + "_m" + str(m) + "_" + str(bitn) + "bit_" + 'finite.tif' + "/" + picNames[i] + "_" + str(lowPercentClip) + "_" + str(highPercentClip) + "_m" + str(m) + "_" + str(bitn) + "bit_" + name + '.tif', outArray[i], photometric = "rgb")
    except FileExistsError:
        print("Directory " , directory ,  " already exists")
print(time.process_time() - start)    
