#!/usr/bin/python

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab

import os

class Evaluate:
    def __init__(self, logDir, values):
        fig = plt.figure(figsize=(7,3.7))
        plt.subplots_adjust(left=0.11, bottom=0.16, right=0.94, top=0.90, wspace=0.29, hspace=0.20)


        ######################################################################################
        # CDF 

        for i, (kValue, lValue, emdValue) in enumerate(values):
            kEmdValues = self.loadEmdValues( logDir + ("kanonymity_orgEmdValues_%d.txt" % kValue))
            lEmdValues = self.loadEmdValues( logDir + ("ldiversity_orgEmdValues_%d.txt" % lValue))
            emdEmdValues = self.loadEmdValues(logDir + ("closeness_orgEmdValues_%lf.txt" % emdValue))

            ax = fig.add_subplot(1, 2, i+1)

            bins = [x*0.01 for x in range(0,100,1)]

            n, bins, patches = ax.hist(kEmdValues, bins=bins, normed=1, color='b', 
                    histtype='step', cumulative=True, label='$k$=%d' % kValue, linestyle='dotted', linewidth=1.5)

            n, bins, patches = ax.hist(lEmdValues, bins=bins, normed=1, color='g', 
                    histtype='step', cumulative=True, label='$l$=%d' % lValue, linestyle='dashed', linewidth=1.5)

            n, bins, patches = ax.hist(emdEmdValues, bins=bins, normed=1, color='r',
                    histtype='step', cumulative=True, label='$\\theta_t$=%.2lf' % emdValue, linestyle='solid', linewidth=1.5)

            #ax.set_ylabel('CDF')
            ax.set_ylabel('CDF')
            ax.set_xlabel('EMD')
            ax.set_xlim(0,0.3)
            ax.set_xticks([0,0.1,0.2,0.3])
            ax.set_ylim(0,1.00)
            ax.legend(loc=4, numpoints=1 )



        ######################################################################################
        # PDF k
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

        ######################################################################################
        plt.savefig('image/compareSingle.eps', format='eps')
        plt.savefig('image/compareSingle.png', format='png')

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


if __name__ == "__main__":
    #logDir = "./rich/"
    #logDir = "./secret/"
    logDir = "./boa/"

    #evaluate = Evaluate(logDir, [(10,10,0.040), (23,25,0.010)])
    evaluate = Evaluate(logDir, [(16,7,0.05), (43,18,0.02)])

