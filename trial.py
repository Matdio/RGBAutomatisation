pre = 15500
high = 2148
low = 1569

bright = (pre - low)/(high - low)

if bright <= 0:
    bright = 0
if bright >= 0:
    bright = 1
    
col = int(bright * 2**16)
print(col)