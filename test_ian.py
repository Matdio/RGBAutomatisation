from astropy.io import fits
import numpy

#define hdul
image_position = "fits/first_fit.fit"
hdul = fits.open(image_position)

#get resolution and check if resolution is divisible by 2 and is odd
def check_res(res):
    if (res % 2) == 0:
        return res
    else:
        res -= 1
        check_res(res)

resx = check_res(hdul[0].header[3])
resy = check_res(hdul[0].header[4])

#define data as an array
data = hdul[0].data

