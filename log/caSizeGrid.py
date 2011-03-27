#!/usr/bin/python

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab

import os

class Evaluate:
    def __init__(self, logDir, kValues, lValues, emdValues ):
        fig = plt.figure(figsize=(9,4))
        plt.subplots_adjust(left=0.07, bottom=0.14, right=0.97, top=0.90, wspace=0.20, hspace=0.20)


        #obtainEmdValues,obtainCaSizes = self.loadEmdCAsizeValues(logDir + ("closeness_obtainedEmdValues_%lf.txt" % emdValue))

        x_limit = 400
        y_limit = 0.4

        ######################################################################################
        # k values
        for i, kValue in enumerate( kValues):
            kEmdValues,kCaSizes = self.loadEmdCAsizeValues(logDir + ("kanonymity_orgEmdValues_%d.txt" % kValue))

            ax = fig.add_subplot(3, 3, i+1)
            ax.plot(kCaSizes, kEmdValues, 'o', markersize=3)
            ax.grid()
            ax.set_xlim(0,x_limit)
            #ax.set_xticks([0,100,200])
            ax.set_ylim(0,y_limit)
            ax.set_title("$k$ = %d" % kValue)

        ######################################################################################
        # l values
        for i, lValue in enumerate( lValues):
            lEmdValues,lCaSizes = self.loadEmdCAsizeValues(logDir + ("ldiversity_orgEmdValues_%d.txt" % lValue))

            ax = fig.add_subplot(3, 3, i+4)
            ax.plot(lCaSizes, lEmdValues, 'o', markersize=3)
            ax.grid()
            ax.set_xlim(0,x_limit)
            #ax.set_xticks([0,100,200])
            ax.set_ylim(0,y_limit)
            ax.set_title("$l$ = %d" % lValue)

        ######################################################################################
        # emd values
        for i, emdValue in enumerate( emdValues):
            ax = fig.add_subplot(3, 3, i+7)
            orgEmdValues,orgCaSizes = self.loadEmdCAsizeValues(logDir + ("closeness_orgEmdValues_%lf.txt" % emdValue))

            ax.plot(orgCaSizes, orgEmdValues, 'o', markersize=3)
            ax.grid()
            ax.set_xlim(0,x_limit)
            #ax.set_xticks([0,100,200])
            ax.set_ylim(0,y_limit)
            #ax.set_xlabel('Size of Cloaking Area')
            #ax.set_ylabel('EMD')
            #ax.set_title('(a) original')
            #ax.legend()
            ax.set_title("$emd$ = %.3lf" % emdValue)


        ######################################################################################
        plt.savefig('image/caSizeGrid.eps', format='eps')
        plt.savefig('image/caSizeGrid.png', format='png')

        plt.show()
        return

    def loadEmdCAsizeValues( self, filename ):
        emdValues = []
        caSizes = []
        fstr = open(filename).read()

        failedNum = 0
        for line in fstr.split("\n"):
            if line == "":
                continue
            if len(line.split(" ")) == 3:
                isFailed = line.split(" ")[1]
                if isFailed == "False":
                    emdValues.append( float(line.split(" ")[0]))
                    caSizes.append( int(line.split(" ")[2]))
                else:
                    emdValues.append( float(line.split(" ")[0]))
                    caSizes.append( int(line.split(" ")[2]))
                    failedNum = failedNum + 1
            else:
                print "ERROR"
        print failedNum
        return emdValues, caSizes


if __name__ == "__main__":
    #logDir = "./rich/"
    #logDir = "./secret/"
    #logDir = "./rainbow/"
    logDir = "./boa/"

    kValues = [5,7,10]
    lValues = [5,7,10]
    emdValues = [0.100, 0.080, 0.040]
    evaluate = Evaluate(logDir, kValues, lValues, emdValues )

