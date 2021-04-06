from astropy.io import fits
import numpy as np

image_position = "fits/first_fit.fit"
hdul = fits.open(image_position)
hdul.info()

data = hdul[0].data



resx = 5202
resy = 3464

fact = 1

output = []

for i in range(int(resy/2)):
    xes = []
    for j in range(int(resx/2)):
        #bggr
        xes.append((int(data[i*2][j*2]*fact), int((data[i*2][j*2-1] + data[i*2-1][j*2])/2), int(data[i*2-1][j*2-1])))
        #rggb
        #xes.append((data[i*2-1][j*2-1], (data[i*2][j*2-1] + data[i*2-1][j*2])/2, data[i*2][j*2]*fact))
        
    output.append(xes)
    
    
outArray = np.array(output)  
