from astropy.io import fits
import numpy as np
import tifffile as tiff
import time
import os
import multiprocessing
import colorsys
from operator import itemgetter
start = time.process_time()

#variables
colMult = 3

redF, greenF, blueF = 1,1,1


death = 0

bitn = 8
bitIn = 16

calibrate = 1

method = 2
#method 0 = rgbOnlyRGB 1 = ALLRGB 2 = rgbonlyHSV


picNames = ["rgb", "r", "g", "b", "g1", "g2"]

nameMain = "RGBHSV2031SClipCalibNO"


m = 0.02

n = 32

output = []
image_position = "fits/second_fit.fit"

lowPercentClip = 60
highPercentClip = 100

mpQueue = multiprocessing.Queue()
Processes = []

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

#function for stretching
def stretchingFunction(x, m):
    if x == 0:
        return 0
    elif x == m:
        return 0.5
    elif x == 1:
        return 1
    else:
        return ((m-1)*x)/((((2*m)-1)*x)-m)



#RGB Transform and Stretch OUTPUT ALL
#[0] = coloured [1] = red [2] = greenAVG [3] = blue [4] = green1 [5] = green2
    
def colourCalibration(data):
    red = []
    green = []
    blue = []
    for i in range(int(resy/2)):
        for j in range(int(resx/2)):
            red.append(data[i*2+1][j*2])
            green.append((data[i*2][j*2]+data[i*2+1][j*2+1])/2)
            blue.append(data[i*2][j*2+1])
        if i%100 == 0:
            print(i)
            
    redPart = np.mean(red)
    greenPart = np.mean(green)
    bluePart = np.mean(blue)
    if redPart <= greenPart and redPart <= bluePart:
        greenFact = redPart/greenPart
        blueFact = redPart/bluePart
        redFact = 1
    if greenPart >= redPart and redPart >= bluePart:
        blueFact = greenPart/bluePart
        redFact = greenPart/redPart
        greenFact = 1
    if bluePart >= redPart and bluePart >= greenPart:
        redFact = bluePart/redPart
        greenFact = bluePart/greenPart
        blueFact = 1
    print("colourCal done")
    return redFact, greenFact, blueFact
        
            
            
    
def TransformStretchHSV(resx, resy, data, bitn, m, low, high, y, n, mpQueue):
    global tOutput
    global bitIn
    global redF, greenF, blueF
    
    #defines start and stop range for current Process
    start = int(((resy/(2*(n)))*y))
    stop = int((resy/(2*(n)))*(y+1))
    
    #final two dimensional list of image part of the current process
    output = []

    for i in range(start, stop):
        xes = []
        for j in range(int(resx / 2)):
            
            #define the grid of the bayer-pattern
            pix0 = data[i*2][j*2]
            pix1 = data[i*2][j*2+1]
            pix2 = data[i*2+1][j*2]
            pix3 = data[i*2+1][j*2+1]
            
            #defines which pixel corresponds to which colour
            preRa = pix2
            preGa= (pix0 + pix3)/2
            preBa = pix1
            
            #RGB-HSV (green/red/blue-F is for colorCalibration
            hsv = colorsys.rgb_to_hsv(preRa*redF, preGa*greenF, preBa*blueF)
            
            #Normalisation of clipped range
            bright = (hsv[2] - low)/ (high - low)
            
            
            #clipping of normalised values
            if bright < 0:
                bright = 0 
            if bright > 1:
                bright = 1
                
            #stretching of clipped values    
            bright = stretchingFunction(bright, m) 
            
            #HSV-RGB (2**bitn-1 is for getting the 0-1 normalised floats to [bitn]-bit vallues)
            newRGB = colorsys.hsv_to_rgb(hsv[0], hsv[1], bright *(2**bitn-1))
            
            
            xes.append(newRGB)
        
        #prints Progress after every 100 rows
        if (i % 100) == 0:
            print(i)
            pass
        
        output.append(xes)
        
    #Queues the number of the Process and the output list
    output = [y, output]
    mpQueue.put(output)
    
    
def TransformStretchALL(resx, resy, data, bitn, m, low, high, y, n, mpQueue):
    global tOutput
    start = int(((resy/(2*(n)))*y))
    stop = int((resy/(2*(n)))*(y+1))
    output = [[],[],[],[],[],[]]
    fact = 1
    for i in range(start, stop):
        xes = [[],[],[],[],[],[]]
        for j in range(int(resx / 2)):
            pix0 = data[i*2][j*2]
            pix1 = data[i*2][j*2+1]
            pix2 = data[i*2+1][j*2]
            pix3 = data[i*2+1][j*2+1]
            preRa = pix2
            preGa= (pix0 + pix3)/2
            preBa = pix1
            preR = (preRa - low)/ (high - low)
            preG = (preGa - low)/ (high - low)
            preB = (preBa - low)/ (high - low)
            preG1a = data[i*2][j*2+1]
            preG2a = data[i*2+1][j*2]
            preG1 = (preG1a - low)/ (high - low)
            preG2= (preG2a - low)/ (high - low)
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
            
            r = int(stretchingFunction(preR*fact, m)*(2**bitn-1))
            g = int(stretchingFunction(preG*fact, m)*(2**bitn-1))
            b = int(stretchingFunction(preB*fact, m)*(2**bitn-1))
            g1 = int(stretchingFunction(preG1*fact, m)*(2**bitn-1))
            g2 = int(stretchingFunction(preG2*fact, m)*(2**bitn-1))
            

            
            xes[0].append((r, g, b))
            xes[1].append((r, 0, 0))
            xes[2].append((0, g, 0))
            xes[3].append((0, 0, b))
            xes[4].append((0, g1, 0))
            xes[5].append((0, g2, 0))
            
            
        if (i % 100) == 0:
            print(i)
            pass
        for i in range(len(output)):    
            output[i].append(xes[i])
    output = [y, output]
    mpQueue.put(output)
    
def TransformStretch(resx, resy, data, bitn, m, low, high, y, n, mpQueue):
    global tOutput
    start = int(((resy/(2*(n)))*y))
    stop = int((resy/(2*(n)))*(y+1))
    output = []
    fact = 1
    for i in range(start, stop):
        xes = []
        for j in range(int(resx / 2)):
            pix0 = data[i*2][j*2]
            pix1 = data[i*2][j*2+1]
            pix2 = data[i*2+1][j*2]
            pix3 = data[i*2+1][j*2+1]
            preRa = pix2
            preGa= (pix0 + pix3)/2
            preBa = pix1
            preR = (preRa - low)/ (high - low)
            preG = (preGa - low)/ (high - low)
            preB = (preBa - low)/ (high - low)
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
            r = int(stretchingFunction(preR*fact, m)*(2**bitn-1))
            g = int(stretchingFunction(preG*fact, m)*(2**bitn-1))
            b = int(stretchingFunction(preB*fact, m)*(2**bitn-1))
            xes.append((r, g, b))
            
        if (i % 100) == 0:
            print(i)
            pass
            
        output.append(xes)
    output = [y, output]
    mpQueue.put(output)

def multiProcessingHSV(resx, resy, data, bitn, m, lowerClip, higherClip, n):
    global Processes, mpQueue
    results = []
    final = []
    for i in range(n):
        Processes[i] = multiprocessing.Process(target=TransformStretchHSV, args=(resx, resy, data, bitn, m, lowerClip, higherClip, i, n, mpQueue,))
        Processes[i].start()
        
    
    for i in range(n):
        results.append(mpQueue.get())
        
    results.sort(key=itemgetter(0))
    
    for i in range(len(results)):
        final.extend(results[i][1])
        
        

        
    
    
        
    for p in Processes:
        
        if death == 0:
            p.join()
            p.terminate()
    return final

def multiProcessing(resx, resy, data, bitn, m, lowerClip, higherClip, n):
    global Processes, mpQueue
    results = []
    final = []
    for i in range(n):
        Processes[i] = multiprocessing.Process(target=TransformStretch, args=(resx, resy, data, bitn, m, lowerClip, higherClip, i, n, mpQueue,))
        Processes[i].start()
        
    for i in range(n):
        results.append(mpQueue.get())
        
    results.sort(key=itemgetter(0))
    
    for i in range(len(results)):
        final.extend(results[i][1])
    
        
    for p in Processes:
        
        if death == 0:
            p.join()
            p.terminate()
    return final



def multiProcessingAll(resx, resy, data, bitn, m, lowerClip, higherClip, n):
    global Processes, mpQueue
    results = []
    final = []
    for i in range(n):
        Processes[i] = multiprocessing.Process(target=TransformStretchALL, args=(resx, resy, data, bitn, m, lowerClip,
                                                                                  higherClip, i, n, mpQueue,))
        Processes[i].start()
    
        
    for i in range(n):
        results.append(mpQueue.get())
        
    results.sort(key=itemgetter(0))
    
    for i in range(len(results)):
        final.append(results[i][1])
        
    results = final
    final = [[],[],[],[],[],[]]
    for i in range(len(results)):
        for j in range(len(results[i])):
            print(j)
            final[j].extend(results[i][j])
    for p in Processes:
        
        if death == 0:
            p.join()
            p.terminate()
    return final
    
    
if __name__ == '__main__':

    needed_data()

    lowerClip = np.percentile(data, lowPercentClip)
    higherClip = np.percentile(data, highPercentClip)
    print(lowerClip, higherClip)
    
    if calibrate == 1:
        redF, greenF, blueF = colourCalibration(data)
        
    else:
        redF, greenF, blueF = 1,1,1
        
    print(redF, greenF, blueF)


    #output = TransformStretch(resx, resy, data, bitn, m, lowerClip, higherClip, 0, 4)
    if method == 0:
        output = multiProcessing(resx, resy, data, bitn, m, lowerClip, higherClip, n)
    elif method == 1:
        output = multiProcessingAll(resx, resy, data, bitn, m, lowerClip, higherClip, n)
    elif method == 2:
        output = multiProcessingHSV(resx, resy, data, bitn, m, lowerClip, higherClip, n)
        



    if method == 0 or method == 2:
        outArray = np.array(output, "uint" + str(bitn))
    elif method == 1:
        outArray = [[],[],[],[],[],[]]
        for i in range(len(output)):
            #print(i)
            outArray[i] = np.array(output[i], "uint" + str(bitn))

    ##print(outArray)
    #print(time.process_time() - start)

    if method == 0:
        tiff.imwrite(str(lowPercentClip) + "_" + str(highPercentClip) + "_m" + str(m) + "_" + str(bitn) + "bit_" + nameMain  + '.tif', outArray, photometric='rgb')
        
    elif method == 1:
        directory = "ALL_" + str(lowPercentClip) + "_" + str(highPercentClip) + "_m" + str(m) + "_" + str(bitn) + "bit_" + nameMain + ".tif"
        try:
            # Create target Directory
            os.mkdir(directory)
            #print("Directory " , directory ,  " Created ") 
            for i in range(len(picNames)):
                tiff.imwrite(directory + "/" + picNames[i] + "_" + str(lowPercentClip) + "_" + str(highPercentClip) + "_m" + str(m) + "_" + str(bitn) + "bit_" + nameMain + '.tif', outArray[i], photometric = "rgb")
        except FileExistsError:
            print("Directory " , directory ,  " already exists")
    
    elif method == 2:
        tiff.imwrite(str(lowPercentClip) + "_" + str(highPercentClip) + "_m" + str(m) + "_" + str(bitn) + "bit_" + nameMain + "smooth"   + '.tif', outArray, photometric='rgb')
    
    print(time.process_time() - start)    
    print("done")