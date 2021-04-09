from astropy.io import fits
import numpy as np
import tifffile as tiff
import multiprocessing
import time

#variables
bitn = 16
bitIn = 16

m = 0.05
n = 4

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
def TransformStretch1(resx, resy, data, bitIn, m, y, yi, q):
    output = []
    fact = 1/(2**bitIn)
    for i in range(int(y//2)):
        i += (y*yi)//2
        xes = []
        for j in range(int(resx / 2)):
            r = mappingFunction(data[i*2-1][j*2-1]*fact, m)*(2**bitIn)
            g = mappingFunction(((data[i*2][j*2-1] + data[i*2-1][j*2])/2)*fact, m)*(2**bitIn)
            b = mappingFunction(data[i*2][j*2]*fact, m)*(2**bitIn)
            xes.append((r, g, b))
            
        if (i % 100) == 0:
            print(i)
        output.append(xes)
    print("Process done: " + str(yi))
    q.put(output)
    return
    


    """if int(y) == 0:
        output1 = output
    elif int(y) != 0:
        output2 = output"""

    
def split_array(x):
    print(resx, resy)
    x1 = resy//x
    return(x1)

def start_multithreading(resx, resy, data, bitIn, m):
    q = multiprocessing.Queue()
    y = split_array(n)
    print("t: " + str(y))
    threads = []
    final = []
    print("break1")
    if __name__ == '__main__':
        for i in range(n):
            threads.append(multiprocessing.Process(target=TransformStretch1, args=(resx, resy, data, bitIn, m, y, i, q,)))
            threads[i].start()
        
        for i in range(n):
            queue = None
            print("break3")
            queue = q.get()
            print("Output of Process " + str(i))
            final.extend(queue)
            print("final got extended")
        
        for i in range(n):
            threads[i].join()
            print("break4")
        
        for i in range(n):
            print("break5")
    
    return(final)
    

needed_data()
output = start_multithreading(resx, resy, data, bitIn, m)
outArray = np.array(output, "uint16")
print("done")

tiff.imwrite('finite.tif', outArray, photometric='rgb')