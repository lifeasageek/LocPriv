#!/usr/bin/python

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab

import os

TOTAL_QUERY_SIZE = 4000

class Evaluate:
    def __init__(self, logDir):
        self.fig = plt.figure(figsize=(9,3.5))
        #self.fig = plt.figure()
        plt.subplots_adjust(left=0.07, bottom=0.13, right=0.97, top=0.88, wspace=0.25, hspace=0.20)

        #thetaList = list(np.arange(0, 0.3, 0.025))
        #thetaList = list(np.arange(0, 0.6, 0.05))
        #thetaList = list(np.arange(0, 0.24, 0.02))
        #hetaList = [0.15, 0.10, 0.05]
        #thetaList = [0.15, 0.10, 0.05]
        thetaList = [0.150, 0.100, 0.050]

        for i, theta in enumerate(thetaList):
            self.caSize_vs_emd(theta, (len(thetaList)/3,3,i+1))




        plt.savefig('image/insecureCA.eps', format='eps')
        plt.savefig('image/insecureCA.png', format='png')

        plt.show()
        return

    def caSize_vs_emd(self,theta, (numRows, numCols, numPos)):
        ax = self.fig.add_subplot(numRows, numCols, numPos)
        if numPos == 1:
            ax.set_title( '(a) $\\theta_a$ = %.2f' % theta)
        if numPos == 2:
            ax.set_title( '(b) $\\theta_a$ = %.2f' % theta)
        if numPos == 3:
            ax.set_title( '(c) $\\theta_a$ = %.2f' % theta)

        ax.set_aspect('normal')

        emd_values, l_values, k_values, cellSize = self.loadLogs(logDir)

	emd_values.remove(0.01)
	k_values.remove(50)
        #l_values.remove(1)
        #k_values.remove(24)
        #k_values.remove(25)
        #k_values.remove(1)

        k_x = []
        k_y = []

        for i, k_value in enumerate(k_values):
            #self.title = "L %d, %d" % (l_value, cellSize[l_value])
            vulnCount = self.countThetaVulnEmdValues( logDir + ("kanonymity_orgEmdValues_%d.txt" % k_value), theta) 
            x = cellSize[('k'), k_value]
            y = vulnCount
            print "k :", k_value, x, y

            k_x.append(x)
            k_y.append(y)

            if numPos == 1 and k_value in [16]:
                ax.text( x, y+150, str(k_value))
            if numPos == 2 and k_value in [16,43]:
                ax.text( x, y+150, str(k_value))
            if numPos == 3 and k_value in [16,43]:
                ax.text( x, y+150, str(k_value))


        l_x = []
        l_y = []
        for l_value in l_values:
            if l_value > 18:
                continue
            #self.title = "L %d, %d" % (l_value, cellSize[l_value])
            vulnCount = self.countThetaVulnEmdValues( logDir + ("ldiversity_orgEmdValues_%d.txt" % l_value), theta) 
            x = cellSize[('l'), l_value]
            y = vulnCount
            print "l :", l_value, x, y

            l_x.append(x)
            l_y.append(y)

            if numPos == 1 and l_value in [7]:
                ax.text( x, y-400, str(l_value))
            if numPos == 2 and l_value in [7,18]:
                ax.text( x, y-300, str(l_value))
            if numPos == 3 and l_value in [7,18]:
                ax.text( x, y-400, str(l_value))


        emd_x = []
        emd_y = []
        for emd_value in emd_values:
            #self.title = "EMD %lf, %d" % (emd_value, cellSize[emd_value])
            vulnCount = self.countThetaVulnEmdValues( logDir + ("closeness_orgEmdValues_%lf.txt" % emd_value), theta)
            x = cellSize[('c',emd_value)]
            y = vulnCount
            print "emd :", emd_value, x, y

            #ax.plot( x, y, 'ro')
            #ax.plot( x, y, linestyle='None', marker='o', color='w', markersize=10)
            emd_x.append(x)
            emd_y.append(y)

            if numPos == 1 and emd_value in [0.10]:
                ax.text( x, y, str(emd_value))
            if numPos == 2 and emd_value in [0.1, 0.05, 0.02]:
                ax.text( x, y, str(emd_value))
            if numPos == 3 and emd_value in [0.05, 0.02]:
                ax.text( x, y, str(emd_value))



        l1 = ax.plot( k_x, k_y, linestyle='-', marker='<', color='b', markeredgecolor='b', markerfacecolor='w', markersize=5)
        l2 = ax.plot( l_x, l_y, linestyle='-', marker='D', color='g', markeredgecolor='g', markerfacecolor='w', markersize=5)
        l3 = ax.plot( emd_x, emd_y, linestyle='-', marker='o', color='r', markersize=5)

        if numPos != 3:
            ax.legend((l1, l2, l3), ('$k$','$l$','$\\theta_t$'), loc=1, numpoints=1 )


        #if numPos == 1:
            #ax.set_ylim(0, 4500)
            #ax.set_yticks([0,1000,2000,3000,4000])
        #if numPos == 2:
            #ax.set_ylim(0, 4500)
            #ax.set_yticks([0,1000,2000,3000,4000])
        #if numPos == 3:
            #ax.set_ylim(0, 4500)
            #ax.set_yticks([0,1000,2000,3000,4000])
        ax.plot([120, 120], [0,4500], linestyle=':', color='k', linewidth=1)
        ax.plot([42, 42], [0,4500], linestyle=':', color='k', linewidth=1)

        ax.set_xlim(0, 150)
        ax.set_xticks([ 0, 50, 100,150])

        ax.set_ylim(0, 4500)
        ax.set_yticks([0,1000,2000,3000,4000])
        ax.set_yticklabels([0,1.0,2.0,3.0,4.0])


        #ax.grid()

        #ax.set_xlabel('Avg. size of cloaking area')
        #ax.set_ylabel('# of $\\theta$-insecure cloaking areas')

        return

    def countThetaVulnEmdValues( self, filename, theta):
        vulnCount = 0

        fstr = open(filename).read()
        for line in fstr.split("\n"):
            if line == "":
                continue
            emdValue =  float(line.split(" ")[0])
            if emdValue > theta:
                vulnCount = vulnCount + 1
        return vulnCount

    def getCellSize( self, filename):
        fstr = open(filename).read()
        for line in fstr.split("\n"):
            if line.startswith("sumQueryCellSize"):
                #print line
                cellSize = int(line.split(":")[1])
                return cellSize *1.0 / TOTAL_QUERY_SIZE
        return -1

    def loadLogs( self, logDir):
        emd_values = []
        l_values = []
        k_values = []

        cellSize = {}

        for filename in os.listdir(logDir):
            if filename.startswith("kanonymity_stat"):
                k_value = int(filename.split("_")[2][:-4])
                k_values.append(k_value)
                cellSize[('k', k_value)] = self.getCellSize(logDir + filename)

            if filename.startswith("closeness_stat"):
                emd_value = float(filename.split("_")[2][:-4])
                emd_values.append(emd_value)
                cellSize[('c', emd_value)] = self.getCellSize(logDir + filename)

            if filename.startswith("ldiversity_stat"):
                l_value = int(filename.split("_")[2][:-4])
                l_values.append(l_value)
                cellSize[('l', l_value)] = self.getCellSize(logDir + filename)

        print "k_values :", k_values
        print "l_values :", l_values
        print "emd_values :", emd_values
        emd_values.sort()
        l_values.sort()
        k_values.sort()

        return emd_values, l_values, k_values, cellSize

if __name__ == "__main__":
    #logDir = "./rich/"
    #logDir = "./secret/"
    #logDir = "./rainbow/"
    logDir = "./boa/"
    evaluate = Evaluate(logDir)

