import os
import shutil

downloadDir= "/path/to/unziped/TACO/batches/"
try:
    os.chdir(downloadDir+"tacoimages")
except:
    os.mkdir(downloadDir+"tacoimages")

countUp = 0
for batch in range(1,16):
    os.chdir(downloadDir)
    path = "batch_"+str(batch)
    buffer = []
    print(os.getcwd())
    for files in os.listdir(path):
        buffer.append(files)
    buffer.sort()
    for files in buffer:
        os.chdir(downloadDir+path)
        strCU = str(countUp)
        countUp+=1
        reName = ""
        for x in range(0,6-len(strCU)):
            reName += "0"
        reName += strCU+".jpg"
        os.rename(files,reName)
        shutil.move(reName,downloadDir+"tacoimages/"+reName)
