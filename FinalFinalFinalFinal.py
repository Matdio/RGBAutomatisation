from astropy.io import fits #not integrated
import numpy as np #not integrated
import tifffile as tiff #not integrated
import os #integrated
import multiprocessing #integrated
import colorsys #integrated
import datetime #integrated
from operator import itemgetter #integrated
"""
Input:
- Image-File (Positon of file (absolut or relativ), image_position)
- Bit-size of brightness value (e.g. 16 or 8, bitIn)
- midtonesbalance (float(0 - 1), m)
- lower border for cliping, percenatge (Integer, lowPercentClip)
- higher border for cliping, percentage (Integer, highPercentClip)
- colour calibration (Integer (1=True, 0=False), calibrate)
"""
#variables

redF, greenF, blueF = 1, 1, 1

death = 0

bitn = 8
bitIn = 16

calibrate = 0

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
    
    #adds respective colour to its list
    for i in range(int(resy/2)):
        for j in range(int(resx/2)):
            red.append(data[i*2+1][j*2])
            green.append((data[i*2][j*2]+data[i*2+1][j*2+1])/2)
            blue.append(data[i*2][j*2+1])
        if i%100 == 0:
            print(i)
    
    
    #calculates means of different colours
    redPart = np.mean(red)
    greenPart = np.mean(green)
    bluePart = np.mean(blue)
    
    #creates factors for each colour bi adjusting the big ones to the small ones
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
        
            
            
"""
MultiProcessing:
    multiProcessing is for the multiProcessing-part of the funciton TransformStretch
    Variables:
    - resx: x-Resolution of CFA after editing to a even number. (Argument, Integer)
    - resy: y-Resolution of CFA after editing to a even number. (Argument, Integer)
    - data: List of brightnesses of pixels of the CFA-file. (Argument, Array)
    - bitn: Bit-size of output. (Argument, Integer)
    - m: Parameter for the stretch-function, midtonesbalance. (Argument, Float)
    - low: Low-percentage to be cliped. (Argument, Percentage/Integer)
    - high: High-percentage to be cliped. (Argument, Percentage/Integer)
    - y: Processnumber (Argument, Integer)
    - n: Number of Processes for the multiProcessing. (Argument, Integer)
    - mpQueue: Queue for/of module multiprocessing, needed to return outputs. (Argument, Queue)
    - bitIn: Bit-size of brightness-values of input-CFA-file. (global, Integer)
    - redF, greenF, blueF: colour calibration Factors. (global, Float)
    - start, stop: defines start and stop range for current Process, needed because of multiProcessing (local, Integer)
    - output: final two dimensional list of image part of the current process. (local, List)
"""    
def TransformStretchHSV(resx, resy, data, bitn, m, low, high, y, n, mpQueue):
    global bitIn
    global redF, greenF, blueF
    
    start = int(((resy/(2*(n)))*y))
    stop = int((resy/(2*(n)))*(y+1))
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

"""
MultiProcessing:
    multiProcessing is for the multiProcessing-part of the funciton TransformStretch
    Variables:
    - resx: x-Resolution of CFA after editing to a even number. (Argument, Integer)
    - resy: y-Resolution of CFA after editing to a even number. (Argument, Integer)
    - data: List of brightnesses of pixels of the CFA-file. (Argument, Array)
    - bitn: Bit-size of output. (Argument, Integer)
    - m: Parameter for the stretch-function, midtonesbalance. (Argument, Float)
    - lowerClip: Low-percentage to be cliped. (Argument, Percentage/Integer)
    - higherClip: High-percentage to be cliped. (Argument, Percentage/Integer)
    - n: Number of Processes for the multiProcessing. (Argument, Integer)
    - Processes: List Processes, pre-generated. (global, List)
    - mpQueue: Queue for/of module multiprocessing. (global, Queue)
    - results: List of the returned values of processes, unsorted. (local, List)
    - final: List of the returned values of processes, sorted. (local, List)   
"""
def multiProcessingHSV(resx, resy, data, bitn, m, lowerClip, higherClip, n):
    global Processes, mpQueue
    results = []
    final = []
    
    #generate all Processes and start them
    for i in range(n):
        Processes[i] = multiprocessing.Process(target=TransformStretchHSV, args=(resx, resy, data, bitn, m, lowerClip, higherClip, i, n, mpQueue,))
        Processes[i].start()
    
    #append returned values of Processes to list results
    for i in range(n):
        results.append(mpQueue.get())
        
    results.sort(key=itemgetter(0))
    
    for i in range(len(results)):
        final.extend(results[i][1])    
    
    #join and close all Processes (without the terminate(), Zombies will be generated)
    #if death not 0 Zombie-Spwaner
    for p in Processes:
        if death == 0:
            p.join()
            p.terminate()
    return final


if __name__ == '__main__':

    needed_data()
    
    
    #transforms Clippercentages into concrete values
    lowerClip = np.percentile(data, lowPercentClip)
    higherClip = np.percentile(data, highPercentClip)
    
    
    #Defines color calibration factors
    if calibrate == 1:
        redF, greenF, blueF = colourCalibration(data)
        
    else:
        redF, greenF, blueF = 1,1,1
        
    
    #executes multiprocessing    
    output = multiProcessingHSV(resx, resy, data, bitn, m, lowerClip, higherClip, n)
    
    
    #transforms two-dimensional list (output) to numpy array
    outArray = np.array(output, "uint" + str(bitn))
    
    #creates image from numpy array
    tiff.imwrite(str(datetime.date.today()) + str(datetime.now.strftime("%X")) +
                 (lowPercentClip) + "_" +
                 str(highPercentClip) + "_m" +
                 str(m) + "_" + str(bitn) + "bit_" +
                 nameMain + "smooth" + '.tif', outArray, photometric='rgb')

