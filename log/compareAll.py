#!/usr/bin/python

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab

import os

class Evaluate:
    def __init__(self, logDir):
        fig = plt.figure()
        emd_values, l_values, cellSize = self.loadLogs(logDir)

        numRows = len(emd_values) + len(l_values)
        numCols = 2
        numPos = 1

        for l_value in l_values:
            self.color = 'red'
            self.title = "L %d, %d" % (l_value, cellSize[l_value])
            self.plotEmdValues( logDir + ("ldiversity_orgEmdValues_%d.txt" % l_value) ,fig, (numRows,numCols,numPos))
            numPos = numPos + 1

            self.plotEmdValues( logDir + ("ldiversity_orgEmdValues_%d.txt" % l_value), fig, (numRows,numCols,numPos), isCDF=True)
            numPos = numPos + 1

        for emd_value in emd_values:
            self.color = 'green'
            self.title = "EMD %lf, %d" % (emd_value, cellSize[emd_value])
            self.plotEmdValues( logDir + ("closeness_orgEmdValues_%lf.txt" % emd_value), fig, (numRows,numCols,numPos))
            numPos = numPos + 1
            self.plotEmdValues( logDir + ("closeness_orgEmdValues_%lf.txt" % emd_value), fig, (numRows,numCols,numPos), isCDF=True)
            numPos = numPos + 1
            #plotEmdValues( logDir + "closeness_obtainedEmdValues.txt", fig, 223)
            #plotCDFEmdValues( logDir + "closeness_obtainedEmdValues.txt", fig, 224)

        plt.show()
        return

    def plotEmdValues( self, filename, fig, (numRows, numCols, numPos), isCDF = False):
        emdValues = []
        fstr = open(filename).read()
        for line in fstr.split("\n"):
            if line == "":
                continue
            emdValues.append( float(line))


        ax = fig.add_subplot(numRows, numCols, numPos)

        if isCDF==False:
            print self.title
            #ax.text(0.5, 0.5, self.title, fontsize=10)
            ax.set_title(self.title, horizontalalignment="left", multialignment='left')

        n, bins, patches = ax.hist(emdValues, 100, normed=1, facecolor=self.color, alpha=0.75, cumulative=isCDF)
        return

    def getCellSize( self, filename):
        fstr = open(filename).read()
        for line in fstr.split("\n"):
            if line.startswith("sumQueryCellSize"):
                print line
                cellSize = int(line.split(":")[1])
                return cellSize
        return -1

    def loadLogs( self, logDir):
        emd_values = []
        l_values = []

        cellSize = {}

        for filename in os.listdir(logDir):
            if filename.startswith("closeness_stat"):
                emd_value = float(filename.split("_")[2][:-4])
                emd_values.append(emd_value)
                cellSize[emd_value] = self.getCellSize(logDir + filename)

            if filename.startswith("ldiversity_stat"):
                l_value = int(filename.split("_")[2][:-4])
                l_values.append(l_value)
                cellSize[l_value] = self.getCellSize(logDir + filename)

        emd_values.sort()
        l_values.sort()

        return emd_values, l_values, cellSize

if __name__ == "__main__":
    #logDir = "./rich/"
    #logDir = "./secret/"
    logDir = "./rainbow/"
    evaluate = Evaluate(logDir)

