#!/usr/bin/python

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab

import os

#TOTAL_QUERY_SIZE = 800
TOTAL_QUERY_SIZE = 4000


class Evaluate:
    def __init__(self, logDir):
        fig = plt.figure(figsize=(5,4))
        plt.subplots_adjust(left=0.16, bottom=0.16, right=0.93, top=0.93, wspace=0.20, hspace=0.20)

        ax = fig.add_subplot(1,1,1)
        emd_values = [0.010, 0.020, 0.030, 0.040, 0.050, 0.060, 0.070, 0.080, 0.090, 0.100]
        markers = ['<', 'D', 'o']
        colors = ['b', 'g', 'r']

        x = []
        y = []
        for i, emd_value in enumerate(emd_values):
            cellSize = self.getCellSize( logDir + ("closeness_stat_%lf.txt" % emd_value))
            x.append(emd_value)
            y.append(cellSize)
            print emd_value, cellSize

        ax.plot( x, y, linestyle='-', marker='o', color='b', markeredgecolor='b', markerfacecolor='b', markersize=10)

        ax.set_xlim(0, 0.11)
        ax.set_xticks([0, 0.02, 0.04, 0.06, 0.08, 0.10])
        ax.set_ylim(0, 250)

        ax.set_xlabel('$\\theta_t$', fontsize='large')
        ax.set_ylabel('Average size of a cloaking area', fontsize='large')

        #ax.legend(loc=1, numpoints=1)
        plt.savefig('image/thetaCasize.eps', format='eps')
        plt.savefig('image/thetaCasize.png', format='png')
        plt.show()
        return

    def getCellSize( self, filename):
        fstr = open(filename).read()
        for line in fstr.split("\n"):
            if line.startswith("sumQueryCellSize"):
                #print line
                cellSize = int(line.split(":")[1])
                return cellSize *1.0 / TOTAL_QUERY_SIZE
        return -1



if __name__ == "__main__":
    #logDir = "./rich/"
    #logDir = "./secret/"
    logDir = "./boa/"
    evaluate = Evaluate(logDir)

