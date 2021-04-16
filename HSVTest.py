import colorsys

bitn = 8
bitIn = 16
def mappingFunction(x, m):
    if x == 0:
        return 0
    elif x == m:
        return 0.5
    elif x == 1:
        return 1
    else:
        return ((m-1)*x)/((((2*m)-1)*x)-m)

m = 0.02
fact = 1
low = 0
high = 65000
preRa = 15300
preGa= 13000
preBa = 6800
hsv = colorsys.rgb_to_hsv(preRa, preGa, preBa)
bright = (hsv[2] - low)/ (high - low)

##print(preG, preG1, preG2, preR)
#time.sleep(1)
if bright <= 0:
    bright = 0
if bright >= 1:
    bright = 1

v = int(mappingFunction(bright*fact, m)*(2**bitn-1))
newRGB = colorsys.hsv_to_rgb(hsv[0], hsv[1], v)
print(newRGB)

