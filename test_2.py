from astropy.io import fits
import numpy as np
import tifffile as tiff

def rgb_to_hsv(r, g, b):
    rc, gc, bc = r/255, g/255, b/255
    cmax = max(rc, gc, bc)
    cmin = min(rc, gc, bc)
    dc = cmax - cmin
    
    if rc == cmax:
        h = 60*(((gc-bc)/dc)%6)
    elif gc == cmax:
        h = 60*(((bc-rc)/dc)+2)
    elif bc == cmax:
        h = 60*(((rc-gc)/dc)+4)
    elif dc == 0:
        h = 0
    
    s = (0 if cmax==0 else dc/cmax)
    
    v = cmax
    
    return((h, s, v))

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


bitn = 16

fact = (2**16-1) / (2**bitn-1)
#fact = 1
output = []

def functions(x1, x2, x3):
    x1 = (2**bitn)*x1**0.5
    x2 = (2**bitn)*x2**0.5
    x3 = (2**bitn)*x3**0.5
    return(x1, x2, x3)

for i in range(int(resy / 2)):
    xes = []
    for j in range(int(resx / 2)):
        #bggr
        #xes.append((int(data[i*2][j*2]*fact), int((data[i*2][j*2-1] + data[i*2-1][j*2])/2), int(data[i*2-1][j*2-1])))
        #rggb
        xes.append(functions(data[i*2-1][j*2-1]*fact, (data[i*2][j*2-1] + data[i*2-1][j*2])/2*fact, data[i*2][j*2]*fact))
        #blue
        #xes.append(int(data[i*2][j*2]*fact))
    if (i % 100) == 0:
        print(i)
    output.append(xes)


    

outArray = np.array(output, "uint" + str(bitn))
print(outArray)

tiff.imwrite('finite.tif', outArray, photometric='rgb')