#!/usr/bin/python

import numpy as np
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab

import os

class Evaluate:
    def __init__(self, logDir, kValues, lValues, emdValues ):
        #fig = plt.figure(figsize=(5.5,9))
        fig = plt.figure(figsize=(7,5.5))
        plt.subplots_adjust(left=0.06, bottom=0.10, right=0.98, top=0.90, wspace=0.10, hspace=0.58)

        self.numBins = 12
        self.xlimit = 300
        self.ylimit = 0.40

        #obtainEmdValues,obtainCaSizes = self.loadEmdCAsizeValues(logDir + ("closeness_obtainedEmdValues_%lf.txt" % emdValue))

        ######################################################################################
        # k values
        for i, kValue in enumerate( kValues):
            kEmdValues, kCaSizes = self.loadEmdCAsizeValues(logDir + ("kanonymity_orgEmdValues_%d.txt" % kValue))

            #ax = fig.add_subplot(3, 2, i+1)
            ax = fig.add_subplot(2, 3, (i*3)+1)
            histMat = self.computeHistMat( kCaSizes, kEmdValues)
            ax.matshow(histMat, cmap=cm.gray)

            ax.get_xaxis().set_ticks_position('bottom')
            ax.set_xticks([0-0.5,self.numBins/2, self.numBins-1])
            ax.set_xticklabels([0,self.xlimit/2, self.xlimit])
            ax.set_yticks([self.numBins-0.5,self.numBins/2, 0])
            ax.set_yticklabels([0, self.ylimit/2, self.ylimit])

            #ax.set_xlabel('Size of cloaking area')
            #ax.set_ylabel('EMD')

            if i == 0:
                ax.set_title('(a1) $k$=%d' % kValue)
            if i == 1:
                ax.set_title('(b1) $k$=%d' % kValue)


        ######################################################################################
        # l values
        for i, lValue in enumerate( lValues):
            lEmdValues,lCaSizes = self.loadEmdCAsizeValues(logDir + ("ldiversity_orgEmdValues_%d.txt" % lValue))

            #ax = fig.add_subplot(3, 2, (i+3))
            ax = fig.add_subplot(2, 3, (i*3)+2)
            histMat = self.computeHistMat( lCaSizes, lEmdValues)
            ax.matshow(histMat, cmap=cm.gray)


            ax.get_xaxis().set_ticks_position('bottom')
            ax.set_xticks([0-0.5,self.numBins/2, self.numBins-1])
            ax.set_xticklabels([0,self.xlimit/2, self.xlimit])
            ax.set_yticks([self.numBins-0.5,self.numBins/2, 0])
            ax.set_yticklabels([0, self.ylimit/2, self.ylimit])

            #ax.set_xlabel('Size of cloaking area')
            #ax.set_ylabel('EMD')

            if i == 0:
                ax.set_title('(a2) $l$=%d' % lValue)
            if i == 1:
                ax.set_title('(b2) $l$=%d' % lValue)



        #######################################################################################
        ## emd values
        for i, emdValue in enumerate( emdValues):
            orgEmdValues,orgCaSizes = self.loadEmdCAsizeValues(logDir + ("closeness_orgEmdValues_%lf.txt" % emdValue))

            #ax = fig.add_subplot(3, 2, i+5)
            ax = fig.add_subplot(2, 3, (i*3)+3)
            histMat = self.computeHistMat( orgCaSizes, orgEmdValues)
            ax.matshow(histMat, cmap=cm.gray)

            ax.get_xaxis().set_ticks_position('bottom')
            ax.set_xticks([0-0.5,self.numBins/2, self.numBins-1])
            ax.set_xticklabels([0,self.xlimit/2, self.xlimit])
            ax.set_yticks([self.numBins-0.5,self.numBins/2, 0])
            ax.set_yticklabels([0, self.ylimit/2, self.ylimit])

            #ax.set_xlabel('Size of cloaking area')
            #ax.set_ylabel('EMD')

            if i == 0:
                ax.set_title('(a3) $\\theta_t$=%.2f' % emdValue)
            if i == 1:
                ax.set_title('(b3) $\\theta_t$=%.2f' % emdValue)


            
        #######################################################################################
        plt.savefig('image/caSizeImshow.eps', format='eps')
        plt.savefig('image/caSizeImshow.png', format='png')

        plt.show()
        return

    def computeHistMat(self, x, y):
        numBins = self.numBins
        hist,xedges,yedges = np.histogram2d(x,y, bins=numBins, range=[[0, self.xlimit], [0.0, self.ylimit]])

        newHist = np.zeros( (numBins, numBins))
        for i in range(numBins):
            for j in range(numBins):
                newHist[numBins-j-1][i] = hist[i][j]


        return newHist

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
                emdValue = float(line.split(" ")[0])
                caSize = int(line.split(" ")[2])

                if str(emdValue) == 'nan':
                    continue

                if isFailed == "False":
                    emdValues.append( emdValue)
                    caSizes.append( caSize)
                else:
                    emdValues.append( emdValue)
                    caSizes.append( caSize)
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

    kValues = [16,43]
    lValues = [7,18]
    emdValues = [0.05, 0.02]
    evaluate = Evaluate(logDir, kValues, lValues, emdValues )

