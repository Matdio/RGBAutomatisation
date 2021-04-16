from astropy.io import fits
import numpy as np
import tifffile as tiff
import time
import os
import multiprocessing
import colorsys
start = time.process_time()

#variables


death = 0

bitn = 16
bitIn = 16


boolAll = 3

picNames = ["rgb", "r", "g", "b", "g1", "g2"]

nameMain = "midtones"


m = 0.02

n = 16

output = []
image_position = "fits/first_fit.fit"

lowPercentClip = 0
highPercentClip = 100

mpQueue = multiprocessing.Queue()
mpQueue2 = multiprocessing.Queue()
mpQueue3 = multiprocessing.Queue()
mpQueue4 = multiprocessing.Queue()
Processes = []
tOutput = [[], [], [], [], [], [], [], []]

for i in range(n):
    Processes.append(0)


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
    
    
    
def TransformStretchHSV(resx, resy, data, bitn, m, low, high, y, n, mpQueue):
    global tOutput
    global bitIn
    start = int(((resy/(2*(n)))*y))
    stop = int((resy/(2*(n)))*(y+1))
    ##print(start, stop)
    output = [[],[],[],[],[],[]]
    fact = 1
    transform = 2**8/bitIn
    for i in range(start, stop):
    #for i in range(int(resy / 2)):
        xes = [[],[],[],[],[],[]]
        for j in range(int(resx / 2)):
            preRa = data[i*2][j*2]
            preGa= (data[i*2][j*2+1] + data[i*2+1][j*2])/2
            preBa = data[i*2+1][j*2+1]
            colorsys.rgb_to_hsv(preRa*transform, preGatransform, preBatransform)
            preR = (preRa - low)/ (high - low)
            preG = (preGa - low)/ (high - low)
            preB = (preBa - low)/ (high - low)
            preG1a = data[i*2][j*2+1]
            preG2a = data[i*2+1][j*2]
            preG1 = (preG1a - low)/ (high - low)
            preG2= (preG2a - low)/ (high - low)
            ##print(preG, preG1, preG2, preR)
            #time.sleep(1)
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
            
            r = int(mappingFunction(preR*fact, m)*(2**bitn-1))
            g = int(mappingFunction(preG*fact, m)*(2**bitn-1))
            b = int(mappingFunction(preB*fact, m)*(2**bitn-1))
            g1 = int(mappingFunction(preG1*fact, m)*(2**bitn-1))
            g2 = int(mappingFunction(preG2*fact, m)*(2**bitn-1))
            
            #print(preR, preRa, r, bitn)
            #time.sleep(1)

            #if isinstance(g, int) == False():
                #quit()
            
            xes[0].append((r, g, b))
            xes[1].append((r, 0, 0))
            xes[2].append((0, g, 0))
            xes[3].append((0, 0, b))
            xes[4].append((0, g1, 0))
            xes[5].append((0, g2, 0))
            
            #print(str(xes[2]))
            
        if (i % 100) == 0:
            print(i)
            #print(str(xes[2]))
            pass
        for i in range(len(output)):    
            output[i].append(xes[i])
    #print(str(len(output)))
    mpQueue.put(output)
def TransformStretchALL(resx, resy, data, bitn, m, low, high, y, n, mpQueue):
    global tOutput
    start = int(((resy/(2*(n)))*y))
    stop = int((resy/(2*(n)))*(y+1))
    ##print(start, stop)
    output = [[],[],[],[],[],[]]
    fact = 1
    for i in range(start, stop):
    #for i in range(int(resy / 2)):
        xes = [[],[],[],[],[],[]]
        for j in range(int(resx / 2)):
            preRa = data[i*2][j*2]
            preGa= (data[i*2][j*2+1] + data[i*2+1][j*2])/2
            preBa = data[i*2+1][j*2+1]
            preR = (preRa - low)/ (high - low)
            preG = (preGa - low)/ (high - low)
            preB = (preBa - low)/ (high - low)
            preG1a = data[i*2][j*2+1]
            preG2a = data[i*2+1][j*2]
            preG1 = (preG1a - low)/ (high - low)
            preG2= (preG2a - low)/ (high - low)
            ##print(preG, preG1, preG2, preR)
            #time.sleep(1)
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
            
            r = int(mappingFunction(preR*fact, m)*(2**bitn-1))
            g = int(mappingFunction(preG*fact, m)*(2**bitn-1))
            b = int(mappingFunction(preB*fact, m)*(2**bitn-1))
            g1 = int(mappingFunction(preG1*fact, m)*(2**bitn-1))
            g2 = int(mappingFunction(preG2*fact, m)*(2**bitn-1))
            
            #print(preR, preRa, r, bitn)
            #time.sleep(1)

            #if isinstance(g, int) == False():
                #quit()
            
            xes[0].append((r, g, b))
            xes[1].append((r, 0, 0))
            xes[2].append((0, g, 0))
            xes[3].append((0, 0, b))
            xes[4].append((0, g1, 0))
            xes[5].append((0, g2, 0))
            
            #print(str(xes[2]))
            
        if (i % 100) == 0:
            print(i)
            #print(str(xes[2]))
            pass
        for i in range(len(output)):    
            output[i].append(xes[i])
    #print(str(len(output)))
    mpQueue.put(output)
    
def TransformStretch(resx, resy, data, bitn, m, low, high, y, n, mpQueue):
    global tOutput
    start = int(((resy/(2*(n)))*y))
    stop = int((resy/(2*(n)))*(y+1))
    ##print(start, stop)
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
            pass
            
        output.append(xes)
    mpQueue.put(output)

def Bilinear(resx, resy, y, n, data, queue1, queue2, queue3, queue4):
    output = []
    if y == 0:
        print(y)
        start = int((resx/n)*(y)+1)
        stop = int((resx/n)*(y+1))
        print((start, stop))
    if y == n-1:
        print(y)
        start = int((resx/n)*(y))
        stop = int((resx/n)*(y+1)-1)
        print((start, stop))
    else:
        print(y)
        start = int((resx/n)*(y))
        stop = int((resx/n)*(y+1))
        print((start, stop))
    for j in range(start, stop):
        xes = []
        for i in range(1, resy-1):
            if i%2 == 0:
                if j%2 == 0:
                    #green1
                    r = int(((data[i][j-1]+data[i][j+1])/2)*((2**bitn-1)/(2**bitIn)))
                    g = int(data[i][j]*((2**bitn-1)/(2**bitIn)))
                    b = int(((data[i-1][j]+data[i+1][j])/2)*((2**bitn-1)/(2**bitIn)))
                    xes.append((r, g, b))
                if j%2 == 1:
                    #blue
                    r = int(((data[i-1][j-1]+data[i-1][j+1]+data[i+1][j+1]+data[i+1][j-1])/4)*((2**bitn-1)/(2**bitIn)))
                    g = int(((data[i-1][j]+data[i][j+1]+data[i+1][j]+data[i][j-1])/4)*((2**bitn-1)/(2**bitIn)))
                    b = int(data[i][j]*((2**bitn-1)/(2**bitIn)))
                    xes.append((r, g, b))
            if i%2 == 1:
                if j%2 == 0:
                    #red
                    r = int(data[i][j]*((2**bitn-1)/(2**bitIn)))
                    g = int(((data[i-1][j]+data[i][j+1]+data[i+1][j]+data[i][j-1])/4)*((2**bitn-1)/(2**bitIn)))
                    b = int(((data[i-1][j-1]+data[i-1][j+1]+data[i+1][j+1]+data[i+1][j-1])/4)*((2**bitn-1)/(2**bitIn)))
                    xes.append((r, g, b))
                if j%2 == 1:
                    #green2
                    r = int(((data[i-1][j]+data[i+1][j])/2)*((2**bitn-1)/(2**bitIn)))
                    g = int(data[i][j]*((2**bitn-1)/(2**bitIn)))
                    b = int(((data[i][j-1]+data[i][j+1])/2)*((2**bitn-1)/(2**bitIn)))
                    xes.append((r, g, b))
        if (j % 100) == 0:
            print(j)
            #print(xes)
        
        output.append(xes)
    print("done with Process: " + str(y))
    #output = (output, y)
    print(len(output))
    queue1.put(output[0:int(len(output)/4)])
    queue2.put(output[int(len(output)/4):int((len(output)*2)/4)])
    queue3.put(output[int((len(output)*2)/4):int((len(output)*3)/4)])
    queue4.put(output[int((len(output)*3)/4):int((len(output)*4)/4)])
                    

def BilinearProcessing(resx, resy, n, data):
    global Processes, mpQueue
    results = []
    xes = []
    print((resx, resy))
    for i in range(n):
        Processes[i] = multiprocessing.Process(target=Bilinear, args=(resx, resy, i, n, data, mpQueue, mpQueue2, mpQueue3, mpQueue4,))
        Processes[i].start()
    print("All Processes started")
    
    for i in range(n):
        out1 = mpQueue.get()
        out2 = mpQueue2.get()
        out3 = mpQueue3.get()
        out4 = mpQueue4.get()
        results.extend(out1)
        results.extend(out2)
        results.extend(out3)
        results.extend(out4)
        print("got data from Process " + str(i))
    
    for p in Processes:
        if death == 0:
            p.join()
            print(str(p) + " joined")
            #results.extend(mpQueue.get())
            #print("got data of " + str(p))
            p.terminate()
        print("Process " + str(p) + " finished")
    return results

def multiProcessing(resx, resy, data, bitn, m, lowerClip, higherClip, n):
    global Processes, mpQueue
    results = []
    for i in range(n):
        Processes[i] = multiprocessing.Process(target=TransformStretch, args=(resx, resy, data, bitn, m, lowerClip, higherClip, i, n, mpQueue,))
        Processes[i].start()
        
    
    for i in range(n):
        print("try to get Queue-Element")
        results.extend(mpQueue.get())
        print("got Queue-Element")
        
    for p in Processes:
        if death == 0:
            p.join()
            p.terminate()
        print("Process " + str(p) + " finished")
    return results
    #print("Done with multiprocessing")



def multiProcessingAll(resx, resy, data, bitn, m, lowerClip, higherClip, n):
    global Processes, mpQueue
    results = []
    final = [[],[],[],[],[],[]]
    for i in range(n):
        Processes[i] = multiprocessing.Process(target=TransformStretchALL, args=(resx, resy, data, bitn, m, lowerClip,
                                                                                  higherClip, i, n, mpQueue,))
        Processes[i].start()
    #print("All Processes started")
    for i in range(n):
        results.append(mpQueue.get())
    #print("got informations")
    #print(str(len(results)), str(len(results[0])))
    for i in range(len(results)):
        for j in range(len(results[i])):
            #print(j)
            final[j].extend(results[i][j])
    #print("edited List")
    for p in Processes:
        
        if death == 0:
            p.join()
            p.terminate()
        #print("Process " + str(p) + " finished")
    return final
    #print("Done with multiprocessing")
    
    
if __name__ == '__main__':

    needed_data()

    lowerClip = np.percentile(data, lowPercentClip)
    higherClip = np.percentile(data, highPercentClip)
    print(lowerClip, higherClip)

    #output = TransformStretch(resx, resy, data, bitn, m, lowerClip, higherClip, 0, 4)
    if boolAll == 0:
        output = multiProcessing(resx, resy, data, bitn, m, lowerClip, higherClip, n)
    if boolAll == 1:
        output = multiProcessingAll(resx, resy, data, bitn, m, lowerClip, higherClip, n)
    if boolAll == 3:
        output = BilinearProcessing(resx, resy, n, data)



    if boolAll == 0:
        outArray = np.array(output, "uint" + str(bitn))
    if boolAll == 1:
        outArray = [[],[],[],[],[],[]]
        for i in range(len(output)):
            #print(i)
            outArray[i] = np.array(output[i], "uint" + str(bitn))
    if boolAll == 3:
        #outArray = np.array(output, "uint16")
        outArray = np.array(output, "uint" + str(bitn))

    ##print(outArray)
    #print(time.process_time() - start)

    if boolAll == 0:
        tiff.imwrite(str(lowPercentClip) + "_" + str(highPercentClip) + "_m" + str(m) + "_" + str(bitn) + "bit_" + nameMain  + '.tif', outArray, photometric='rgb')
        
    else:
        directory = "ALL" + str(lowPercentClip) + "_" + str(highPercentClip) + "_m" + str(m) + "_" + str(bitn) + "bit_" + nameMain + ".tif"
        try:
            # Create target Directory
            os.mkdir(directory)
            #print("Directory " , directory ,  " Created ") 
            for i in range(len(picNames)):
                tiff.imwrite(directory + "/" + picNames[i] + "_" + str(lowPercentClip) + "_" + str(highPercentClip) + "_m" + str(m) + "_" + str(bitn) + "bit_" + nameMain + '.tif', outArray[i], photometric = "rgb")
        except FileExistsError:
            print("Directory " , directory ,  " already exists")
    print(time.process_time() - start)    
    print("done")

