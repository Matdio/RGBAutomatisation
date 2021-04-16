from datetime import datetime

now = datetime.now()
print(str(now.date()) + "_" + str(now.strftime("%H/%M/%S")))