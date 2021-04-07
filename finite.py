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

fact =  (2**bitn-1) / (2**16-1)
print(fact)



def RGBTransform(resx, resy, data, fact):
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


output = RGBTransform(resx, resy, data, fact)
outArray = np.array(output, "uint8")
print(outArray)
print(outArray.dtype)

tiff.imwrite('finite.tif', outArray, photometric='rgb')