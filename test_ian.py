from astropy.io import fits
import numpy

image_position = "fits/first_fit.fit"
hdul = fits.open(image_position)
hdul.info()

data = hdul[0].data
print(data)



resx = 5202
resy = 3465

fact = 1

output = []

for i in range(resx/2):
    xes = []
    for j in range(resy/2):
        xes.append((data[i*2][j*2]*fact, (data[i*2][j*2-1] + data[i*2-1][j*2])/2, data[i*2-1][j*2-1]))
    output.append(xes)