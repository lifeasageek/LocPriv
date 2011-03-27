#!/usr/bin/python

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab

import os

class Evaluate:
    def __init__(self, logDir):
        #fig = plt.figure()
        fig = plt.figure(figsize=(5,4))
        plt.subplots_adjust(left=0.18, bottom=0.15, right=0.93, top=0.90, wspace=0.20, hspace=0.20)

        ax = fig.add_subplot(1,1,1)
        #emd_values = [0.010, 0.020, 0.030, 0.040, 0.050, 0.060, 0.070, 0.080, 0.090, 0.100]
        emd_values = [0.010, 0.020, 0.030, 0.040, 0.050, 0.060, 0.070, 0.080, 0.090, 0.100]
        insecureThetas = [0.020, 0.050, 0.080]
        markers = ['<', 'D', 'o']
        colors = ['b', 'g', 'r']


        for i, insecureTheta in enumerate(insecureThetas):
            x = []
            y = []
            for emd_value in emd_values:
                vulnCount = self.countThetaVulnEmdValues( logDir + ("closeness_orgEmdValues_%lf.txt" % emd_value), insecureTheta)
                x.append(emd_value)
                y.append(vulnCount)

            ax.plot( x, y, linestyle='-', marker=markers[i], color=colors[i], markeredgecolor=colors[i], markeredgewidth=2, markerfacecolor='w', markersize=10, label="$\\theta_a$=%.2f" % insecureTheta, linewidth=1.5)


        #ax.plot([0.00, 0.0575], [466,466], linestyle=':', color='k', linewidth=1)
        ax.plot([0.06, 0.06], [0,437], linestyle=':', color='k', linewidth=1)

        ax.plot([0.08, 0.08], [0,3000], linestyle=':', color='k', linewidth=1)
        ax.plot([0.0, 0.08], [3000,3000], linestyle=':', color='k', linewidth=1)

        #ax.plot([0.00, 0.008], [35,35], linestyle='--', color='k', linewidth=2)
        #ax.plot([0.05, 0.05], [0,30], linestyle='--', color='k', linewidth=2)

        ax.set_xlim(0, 0.15)
        ax.set_xticks([0, 0.02, 0.04, 0.06, 0.08, 0.10, 0.12, 0.14])
        ax.set_ylim(0, 4500)

        ax.set_ylabel('Number of $\\theta_a$-insecure cloaking areas', fontsize='large')
        ax.set_xlabel('$\\theta_t$', fontsize = 'large')

        ax.legend(loc=4, numpoints=1)

        plt.savefig('image/thetaInsecure.eps', format='eps')
        plt.savefig('image/thetaInsecure.png', format='png')
        plt.show()
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


if __name__ == "__main__":
    #logDir = "./rich/"
    #logDir = "./secret/"
    logDir = "./boa/"
    evaluate = Evaluate(logDir)

