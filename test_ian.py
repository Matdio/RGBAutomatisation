from astropy.io import fits
import numpy as np
import tifffile as tif

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


fact = 1

output = []

for i in range(int(resy / 2)):
    xes = []
    for j in range(int(resx / 2)):
        #bggr
        xes.append((int(data[i*2][j*2]*fact), int((data[i*2][j*2-1] + data[i*2-1][j*2])/2), int(data[i*2-1][j*2-1])))
        #rggb
        #xes.append((data[i*2-1][j*2-1], (data[i*2][j*2-1] + data[i*2-1][j*2])/2, data[i*2][j*2]*fact))
    output.append(xes)
    print(i)
    

    
outArray = np.array(output)
print("almost done")
with tif.TiffWriter('temp.tif', bigtiff=True) as tif:
     for i in range(outArray.shape[0]):
         tif.save(outArray[i], compress=6)
