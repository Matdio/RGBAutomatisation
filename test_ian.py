from astropy.io import fits
import numpy as np
import tifffile as tiff

#define hdul
image_position = "fits/first_fit.fit"
hdul = fits.open(image_position)

#get resolution and check if resolution is divisible by 2 and is odd
def check_res(res):
    while (res % 2) != 0:
        res = res - 1
    return(res)

resx = check_res(hdul[0].header[3])
resy = check_res(hdul[0].header[4])

data = hdul[0].data


bitn = 8
bitIn = 16


def mappingFunction(x):
    y = x**0.5
    return y

def RGBTransformToBit(resx, resy, data, bitn, bitIn):
    fact =  (2**bitn-1) / (2**bitIn-1)
    output = []
    for i in range(int(resy / 2)):
        xes = []
        for j in range(int(resx / 2)):
            #bggr
            #xes.append((int(data[i*2][j*2]*fact), int((data[i*2][j*2-1] + data[i*2-1][j*2])/2), int(data[i*2-1][j*2-1])))
            #rggb
            xes.append((data[i*2-1][j*2-1]*fact, ((data[i*2][j*2-1] + data[i*2-1][j*2])/2)*fact, data[i*2][j*2]*fact))
            #blue
            #xes.append(int(data[i*2][j*2]*fact))
        if (i % 100) == 0:
            print(i)
        output.append(xes)
    return output

def RGBTransformTo1(resx, resy, data, bitIn):
    output = []
    fact = 1/bitIn
    for i in range(int(resy / 2)):
        xes = []
        for j in range(int(resx / 2)):
            #bggr
            #xes.append((int(data[i*2][j*2]*fact), int((data[i*2][j*2-1] + data[i*2-1][j*2])/2), int(data[i*2-1][j*2-1])))
            #rggb
            xes.append((data[i*2-1][j*2-1]*fact, ((data[i*2][j*2-1] + data[i*2-1][j*2])/2)*fact, data[i*2][j*2]*fact))
            #blue
            #xes.append(int(data[i*2][j*2]*fact))
        if (i % 100) == 0:
            print(i)
        output.append(xes)
    return output


def RGBTransformNStretch(resx, resy, data, bitIn):
    output = []
    fact = 1/bitIn
    for i in range(int(resy / 2)):
        xes = []
        for j in range(int(resx / 2)):
            #bggr
            #xes.append((int(data[i*2][j*2]*fact), int((data[i*2][j*2-1] + data[i*2-1][j*2])/2), int(data[i*2-1][j*2-1])))
            #rggb
            xes.append((mappingFunction(data[i*2-1][j*2-1]*fact)*(2**bitIn), mappingFunction(((data[i*2][j*2-1] + data[i*2-1][j*2])/2)*fact)*(2**bitIn), mappingFunction(data[i*2][j*2]*fact)*(2**bitIn)))
            #blue
            #xes.append(int(data[i*2][j*2]*fact))
        if (i % 100) == 0:
            print(i)
        output.append(xes)
    return output

def HSVStretch(data):
    stretchedOut = data
    for i in data:
        t = data[i]
        for j in data[i]:
            x = data[i][j][2]
            y = mappingFunction(x)
            t[j][2] = y
        data[i] = t
    return stretchedOut


def RGBStretch(data):
    stretchedOut = data
    for i in data:
        t = data[i]
        for j in data[i]:
            for i in data[i][j]:
                x = data[i][j][k]
                y = mappingFunction(x)
                t[j][k] = y
        data[i] = t
    return stretchedOut
            
            
            
        
output = RGBTransformNStretch(resx, resy, data, bitIn)

outArray = np.array(output, "uint8")
print(outArray)

tiff.imwrite('finite.tif', outArray, photometric='rgb')
