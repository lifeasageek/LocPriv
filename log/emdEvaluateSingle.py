#!/usr/bin/python

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab

import os

class Evaluate:
    def __init__(self, logDir, emdValue):
        #fig = plt.figure()
        fig = plt.figure(figsize=(5,4))
        plt.subplots_adjust(left=0.14, bottom=0.17, right=0.92, top=0.94, wspace=0.20, hspace=0.20)

        orgEmdValues = self.loadEmdValues(logDir + ("closeness_orgEmdValues_%lf.txt" % emdValue))
        obtEmdValues = self.loadEmdValues(logDir + ("closeness_obtainedEmdValues_%lf.txt" % emdValue))

        self.xlimit = 0.2
        self.ylimit = 1.0

        ######################################################################################
        # CDF 
        ax = fig.add_subplot(1, 1, 1)

        bins = [x*0.01 for x in range(0,100,1)]

        n, bins, patches = ax.hist(orgEmdValues, bins=bins, normed=1, color='r', histtype='step', cumulative=True, 
                label='Adversary\'s view', linestyle='solid', linewidth=3)

        n, bins, patches = ax.hist(obtEmdValues, bins=bins, normed=1, color='b', histtype='step', cumulative=True, 
                label='Method\'s view', linestyle='dashed', linewidth=3)

        ax.set_ylabel('CDF')
        ax.set_xlabel('EMD')
        ax.set_xlim(0,self.xlimit)
        ax.set_xticks([0, self.xlimit/4, 0.06,self.xlimit/2, 3*self.xlimit/4, self.xlimit])
        ax.set_xticklabels([0, self.xlimit/4, 0.06,'0.10', 3*self.xlimit/4, '0.20'], rotation=45)

        ax.set_ylim(0,self.ylimit)
        ax.set_yticks([0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0])
        #ax.grid()
        ax.legend(loc=4)

        ######################################################################################
        ax.plot([0.06, 0.06], [0,0.953], linestyle=':', color='k', linewidth=1)
        ax.plot([0.05, 0.05], [0,1.0], linestyle=':', color='k', linewidth=1)

        #ax.plot([0, 0.04], [0.953,0.953], linestyle=':', color='k', linewidth=1)
        ax.plot([0, 0.06], [0.900,0.900], linestyle=':', color='k', linewidth=1)
        #ax.plot([0.05, 0.05], [0,1.0], linestyle=':', color='k', linewidth=1)

        #ax.text(0.028, 0.07, '(a)')
        #ax.text(0.053, 0.2, '(b)')
        #ax.plot([0.06, 0.06], [0,437], linestyle='--', color='k', linewidth=2)

        #######################################################################################
        # PDF 1
        #ax = fig.add_subplot(2, 1, 1)
        #bins = [x*0.01 for x in range(0,100,1)]

        #self.color='red'
        #n, bins, patches = ax.hist(orgEmdValues, bins=bins, normed=1, facecolor=self.color,  histtype='bar', label='original')
        #ax.set_ylabel('PDF')
        #ax.set_xlabel('EMD')

        #ax.set_xlim(0,self.xlimit)
        #ax.set_ylim(0,self.ylimit)
        #ax.set_yticks([0,self.ylimit/2, self.ylimit])
        #ax.set_yticklabels([0,self.ylimit/2/100.0, self.ylimit/100.0])
        #ax.legend(loc=1)

        ########################################################################################
        ### PDF 1
        #ax = fig.add_subplot(2, 1, 2)
        #bins = [x*0.01 for x in range(0,100,1)]

        #self.color='blue'
        #n, bins, patches = ax.hist(obtEmdValues, bins=bins, normed=1, facecolor=self.color,  histtype='bar', label='obtained')
        #ax.set_ylabel('PDF')
        #ax.set_xlabel('EMD')
        #ax.set_xlim(0,self.xlimit)
        #ax.set_ylim(0,self.ylimit)
        #ax.set_yticks([0,self.ylimit/2, self.ylimit])
        #ax.set_yticklabels([0,self.ylimit/2/100.0, self.ylimit/100.0])
        #ax.legend(loc=1)
        #######################################################################################

        plt.savefig('image/emdEvaluateSingle.eps', format='eps')
        plt.savefig('image/emdEvaluateSingle.png', format='png')
        plt.show()
        return


    def loadEmdValues( self, filename ):
        emdValues = []
        fstr = open(filename).read()
        for line in fstr.split("\n"):
            if line == "":
                continue
            if len(line.split(" ")) == 3:
                emdValues.append( float(line.split(" ")[0]))
            else:
                emdValues.append( float(line))
        return emdValues


    def loadLogs( self, logDir):
        emd_values = []

        cellSize = {}

        for filename in os.listdir(logDir):
            if filename.startswith("closeness_stat"):
                emd_value = float(filename.split("_")[2][:-4])
                emd_values.append(emd_value)
                cellSize[emd_value] = self.getCellSize(logDir + filename)

        emd_values.sort()

        return emd_values, cellSize

if __name__ == "__main__":
    #logDir = "./rich/"
    #logDir = "./secret/"
    #logDir = "./rainbow/"
    logDir = "./boa/"
    evaluate = Evaluate(logDir, 0.050)

