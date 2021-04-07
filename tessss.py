from tifffile import imwrite
import numpy 
data = numpy.random.randint(0, 255, (256, 256, 3), 'uint8')
imwrite('temp.tif', data, photometric='rgb')