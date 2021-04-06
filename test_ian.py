from astropy.io import fits
#fits_image_filename = fits.open('first_fit.fit')

hdul = fits.open('fits/first_fit.fit')
hdul.info()