#!/usr/bin/python
import os
import time
import option

def executeOne( cmdStr, (k_values, l_values, emd_values)):
    while 1:
        print cmdStr
        k_values, l_values, emd_values = checkUnexecuted( k_values, l_values, emd_values)
        if len( k_values) + len(l_values) + len(emd_values) == 1:
            os.system(cmdStr)
        time.sleep(5)
    os.exit()
    return

def executeAll(k_values, l_values, emd_values):
    for k_value in k_values:
        cmdStr = "./Kanonymity.py %d " % k_value
        if os.fork() == 0:
            executeOne( cmdStr, ([k_value], [], []))

    for l_value in l_values:
        cmdStr = "./Ldiversity.py %d " % l_value
        if os.fork() == 0:
            executeOne( cmdStr, ([], [l_value], []))

    for emd_value in emd_values:
        cmdStr = "./Closeness.py " + emd_value + " "
        if os.fork() == 0:
            executeOne( cmdStr, ([], [], [emd_value]))
    return

def checkUnexecuted(k_values, l_values, emd_values):
    for filename in os.listdir(logDir):
        if filename.startswith("kanonymity_stat"):
            k_value = int(filename.split("_")[2][:-4])
            try:
                k_values.remove(k_value)
            except:
                pass

        if filename.startswith("ldiversity_stat"):
            l_value = int(filename.split("_")[2][:-4])
            try:
                l_values.remove(l_value)
            except:
                pass

        if filename.startswith("closeness_stat"):
            emd_value = float(filename.split("_")[2][:-4])
            try:
                emd_values.remove("%.3f" % emd_value)
            except:
                pass

    print "k", k_values
    print "l", l_values
    print "emd", emd_values

    return k_values, l_values, emd_values

if __name__ == "__main__":
    #logDir = "./log/rainbow/"
    #logDir = "./log/missa/"
    #logDir = "./log/rainbow/"
    logDir = option.getLogDir()

    k_values = [2,4,6,8,10,12,14,16,18,20,22,24, 26, 30, 33, 35, 40, 43, 45, 50]
    #k_values = [1,3,5,7,9,11,13,15,17,19,21,23,25]
    #k_values = [2,4,6,7,9,23,24,25]
    #l_values = [1,3,5,7,9,11,13,15,17,19,21,23,25]
    l_values = [2,4,6,8,10,12,14,16,18,20,22,24]
    #l_values = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25]
    #l_values = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25]
    emd_values = ['0.010', '0.020', '0.030', '0.040', '0.050', '0.060', '0.070', '0.080', '0.090', '0.100'  ]

    k_values, l_values, emd_values = checkUnexecuted( k_values, l_values, emd_values)
    executeAll( k_values, l_values, emd_values)

