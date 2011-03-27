#!/usr/bin/python

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab

import os

class Evaluate:
    def __init__(self, logDir, kValue, lValue, emdValue ):
        fig = plt.figure(figsize=(9,4))
        plt.subplots_adjust(left=0.07, bottom=0.14, right=0.97, top=0.90, wspace=0.20, hspace=0.20)


        kEmdValues,kCaSizes = self.loadEmdCAsizeValues(logDir + ("kanonymity_orgEmdValues_%d.txt" % kValue))
        lEmdValues,lCaSizes = self.loadEmdCAsizeValues(logDir + ("ldiversity_orgEmdValues_%d.txt" % lValue))
        obtainEmdValues,obtainCaSizes = self.loadEmdCAsizeValues(logDir + ("closeness_obtainedEmdValues_%lf.txt" % emdValue))
        orgEmdValues,orgCaSizes = self.loadEmdCAsizeValues(logDir + ("closeness_orgEmdValues_%lf.txt" % emdValue))

        ######################################################################################
        ax = fig.add_subplot(1, 4, 3)
        ax.plot(kCaSizes, kEmdValues, 'o', markersize=3)
        ax.grid()
        ax.set_xlim(0,200)
        ax.set_xticks([0,100,200])
        ax.set_ylim(0,0.4)

        ax = fig.add_subplot(1, 4, 4)
        ax.plot(lCaSizes, lEmdValues, 'o', markersize=3)
        ax.grid()
        ax.set_xlim(0,200)
        ax.set_xticks([0,100,200])
        ax.set_ylim(0,0.4)

        ax = fig.add_subplot(1, 4, 1)
        ax.plot(orgCaSizes, orgEmdValues, 'o', markersize=4, label='original')
        ax.grid()
        ax.set_xlim(0,200)
        ax.set_xticks([0,100,200])
        ax.set_ylim(0,0.4)

        ax.set_xlabel('Size of Cloaking Area')
        ax.set_ylabel('EMD')
        ax.set_title('(a) original')
        #ax.legend()


        
        ax = fig.add_subplot(1, 4, 2)
        ax.plot(obtainCaSizes, obtainEmdValues, 'o', markersize=4, label='obtained')
        ax.grid()
        ax.set_xlim(0,200)
        ax.set_xticks([0,100,200])
        ax.set_ylim(0,0.4)
        ax.set_xlabel('Size of Cloaking Area')
        ax.set_ylabel('EMD')
        ax.set_title('(b) obtained')
        #ax.legend()
        #ax.set_ylabel('CDF')
        #ax.set_xlabel('EMD')

        #######################################################################################
        ## PDF k
        #ax = fig.add_subplot(4, 1, 2)

        #bins = [x*0.01 for x in range(0,100,1)]

        #self.color='b'
        #n, bins, patches = ax.hist(kEmdValues, bins=bins, normed=1, facecolor=self.color,  histtype='bar', label='$k$')
        #ax.set_ylabel('PDF')
        #ax.set_xlabel('EMD')

        #ax.set_xlim(0,0.5)
        ##ax.set_ylim(0,105)
        #ax.grid()
        #ax.legend(loc=4)

        #######################################################################################
        ## PDF l
        #ax = fig.add_subplot(4, 1, 3)

        #bins = [x*0.01 for x in range(0,100,1)]

        #self.color='g'
        #n, bins, patches = ax.hist(lEmdValues, bins=bins, normed=1, facecolor=self.color,  histtype='bar', label='$l$')
        #ax.set_ylabel('PDF')
        #ax.set_xlabel('EMD')

        #ax.set_xlim(0,0.5)
        ##ax.set_ylim(0,105)
        #ax.grid()
        #ax.legend(loc=4)

        #######################################################################################
        ## PDF emd
        #ax = fig.add_subplot(4, 1, 4)

        #bins = [x*0.01 for x in range(0,100,1)]

        #self.color='r'
        #n, bins, patches = ax.hist(emdEmdValues, bins=bins, normed=1, facecolor=self.color,  histtype='bar', label='$EMD$')
        #ax.set_ylabel('PDF')
        #ax.set_xlabel('EMD')

        #ax.set_xlim(0,0.5)
        ##ax.set_ylim(0,105)
        #ax.grid()
        #ax.legend(loc=4)

        plt.savefig('image/caSize_emd.eps', format='eps')
        plt.savefig('image/caSize_emd.png', format='png')

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
    logDir = "./rainbow/"

    kValue = 5
    lValue = 5
    emdValue = 0.100
    evaluate = Evaluate(logDir, kValue, lValue, emdValue )

