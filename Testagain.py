import numpy as np
import tifffile as tiff

maxx = 100
maxy = 100

outArray = []

for i in range(maxx):
    t = []
    for j in range(maxy):
        if j < (maxy/2):
            t.append((65000,65000,65000))
        else:
            t.append((0,0,0))
    outArray.append(t)
    
outArray = np.array(outArray)
print(outArray)        

tiff.imwrite("trying.tif", data = outArray)
        