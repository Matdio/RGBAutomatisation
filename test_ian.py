from astropy.io import fits
import numpy

image_position = "fits/first_fit.fit"
hdul = fits.open(image_position)
hdul.info()

data = hdul[0].data
print(data)
