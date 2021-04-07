from astropy.io import fits
import numpy as np
import tifffile as tiff
import threading

#variables
bitn = 16
bitIn = 16

m = 0.05

output = []
image_position = "fits/first_fit.fit"


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

#RGB Transform and Stretch
def TransformStretch1(y):
    global output1
    output = []
    fact = 1/(2**bitIn)
    for i in range(y, int((y + (resy/2))/2)):
        i += y
        xes = []
        for j in range(int(resx / 2)):
            r = mappingFunction(data[i*2-1][j*2-1]*fact, m)*(2**bitIn)
            g = mappingFunction(((data[i*2][j*2-1] + data[i*2-1][j*2])/2)*fact, m)*(2**bitIn)
            b = mappingFunction(data[i*2][j*2]*fact, m)*(2**bitIn)
            xes.append((r, g, b))
            
        if (i % 100) == 0:
            print(i)
        output.append(xes)
    output1 = output

def TransformStretch2(y):
    global output2
    output = []
    fact = 1/(2**bitIn)
    for i in range(1732, 3465):
        i += y
        xes = []
        for j in range(int(resx / 2)):
            r = mappingFunction(data[i*2-1][j*2-1]*fact, m)*(2**bitIn)
            g = mappingFunction(((data[i*2][j*2-1] + data[i*2-1][j*2])/2)*fact, m)*(2**bitIn)
            b = mappingFunction(data[i*2][j*2]*fact, m)*(2**bitIn)
            xes.append((r, g, b))
        if (i % 100) == 0:
            print(i)
        output.append(xes)
    output2 = output
    
def split_array(x):
    print(resx, resy)
    return(0, (resy//x))

def start_multithreading(resx, resy, data, bitIn, m):
    y = split_array(2)
    print(y)
    t1 = threading.Thread(target=TransformStretch1, args=(y[0],))
    t2 = threading.Thread(target=TransformStretch2, args=(y[1],))
    
    t1.start()
    t2.start()
    print("No. of active threads: " + str(threading.active_count()))
    #print("break")
    t1.join()
    t2.join()
    output = output1.extend(output2)
    print(output1[0])
    print(output2)
    return(output)
    

needed_data()
output = start_multithreading(resx, resy, data, bitIn, m)
print(output)
outArray = np.array(output, "uint16")
print(outArray)

tiff.imwrite('finite.tif', outArray, photometric='rgb')