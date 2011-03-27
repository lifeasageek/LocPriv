#!/usr/bin/python

import random
import pickle
import scipy

import emd_clone
import matplotlib.pyplot as plt
import numpy as np

#################################################################
class Attack:
    #################################################################
    def __init__(self, logDir, gridSize):
        self.logDir = logDir
        self.gridSize = gridSize

        nodeinfoDict = self.__loadNodeinfo( self.logDir + "/nodeinfo.txt")
        self.grid = self.__createGrid(nodeinfoDict)

        self.__initEMD()
        return

    #################################################################
    def __initEMD(self):
        self.univLocTypesPDF = self.__computePDF([len(x) for x in self.clusteredStayPoints])

        self.emd_module = emd_clone.EMD()

        #self.typeDistanceMat = self.__computeTypeDistanceMatByMean()
        self.typeDistanceMat = self.__computeTypeDistanceMatByDistr()

        #######################################################
        features = range(0,self.numLocTypes)
        self.emd_module.setFeatures( features)

        #flattening
        flatTypeDistanceMat = []
        for dists in self.typeDistanceMat:
            for value in dists: 
                flatTypeDistanceMat.append(value)
        self.emd_module.setTypeDistanceMat(flatTypeDistanceMat) 
        return

    #################################################################
    def __computePDF(self, locTypes):
        totalNum = sum(locTypes)
        if totalNum == 0:
            totalNum = 1
        return [ x*1.0/totalNum for x in locTypes]

    #################################################################
    def computeEMD(self, cellIndexList):
        tmpLocTypes = self.getLocTypes( cellIndexList)
        locTypesPDF = self.__computePDF( tmpLocTypes)

        #print "locTypesPDF : ", locTypesPDF
        #print "univLocTypesPDF :", self.univLocTypesPDF

        emdValue = self.emd_module.computeType( locTypesPDF, self.univLocTypesPDF)
        #print "emd : ", emdValue
        return emdValue


    #################################################################
    def __computeTypeDistanceMatByMean(self ):
        print "computeTypeDistanceMatByMean()"
        fstr = open(self.logDir + "/typeinfo.txt").read()

        typeInfo = {}
        for line in fstr.split("\n"):
            if line == "":
                continue
            items = line.split("\t")
            mu = float(items[1].split(",")[0])
            sigma = float(items[1].split(",")[1])
            typeInfo[ int(items[0])] = float(items[1].split(",")[0])

        maxDistance = max(typeInfo.values()) - min(typeInfo.values())
        D = scipy.zeros( [self.numLocTypes,self.numLocTypes])

        for i in range(self.numLocTypes):
            for j in range(self.numLocTypes):
                distance = abs(typeInfo[i] - typeInfo[j]) / maxDistance
                D[i,j] = distance
        return D

    #################################################################
    def __computeTypeDistanceMatByDistr(self ):
        print "computeTypeDistanceMatByDistr()"
        fstr = open(self.logDir + "/typeinfo.txt").read()

        typeInfo = {}
        for line in fstr.split("\n"):
            if line == "":
                continue
            items = line.split("\t")
            mu = float(items[1].split(",")[0])
            sigma = float(items[1].split(",")[1])

            #print mu, sigma
            typeInfo[ int(items[0])] = (mu, sigma)

        binStep = 20
        maxStayDuration = 400
        binSize = (400/20) - 1
        bins = range(0, 400, binStep)

        stayDurationFeatures = [x+(binStep/2) for x in bins[:-1]]

        #print bins
        #print stayDurationFeatures
        #print "feature length : ", len(stayDurationFeatures)

        self.emd_module.setFeatures( stayDurationFeatures)

        D = scipy.zeros( [self.numLocTypes,self.numLocTypes])
        for i in range(self.numLocTypes):
            (mu1, sigma1) = typeInfo[i]
            x1 = mu1 + sigma1*np.random.randn(10000)
            n1, dummyBins, patches = plt.hist(x1, bins = bins, normed=1, histtype='step')
            distr1 = [x*binStep for x in n1]

            for j in range(self.numLocTypes):
                (mu2, sigma2) = typeInfo[j]
                x2 = mu2 + sigma2*np.random.randn(10000)
                n2, dummyBins, patches = plt.hist(x2, bins = bins, normed=1, histtype='step')
                distr2 = [x*binStep for x in n2]

                e = self.emd_module.computeStaypoint( distr1, distr2)
                #print "-" * 30
                #print mu1, sigma1, mu2, sigma2
                #print distr1, sum(distr1)
                #print distr2, sum(distr2)
                #print len(distr1), len(distr2)
                #print e

                distance = e
                D[i,j] = distance
                print i,j, mu1, sigma1, mu2, sigma2, distance
        return D

    #######################################################
    def getNumLocTypes( self):
        return self.numLocTypes

    #######################################################
    def getCellIndex( self, (x, y)):
        return (self.adjValue(x), self.adjValue(y))


    #######################################################
    def __adjValue( self, value):
        return int(value) / self.gridSize

    #################################################################
    def __createGrid(self, nodeinfoDict):
        grid = {}
        for (x,y), locType in nodeinfoDict.iteritems():
            adjX = self.__adjValue(x)
            adjY = self.__adjValue(y)

            grid[(adjX, adjY)] = grid.get( (adjX,adjY), [0 for x in range(self.numLocTypes)])
            grid[(adjX, adjY)][locType] = grid[(adjX, adjY)][locType] + 1
        return grid

    #######################################################
    def getLocTypes( self, cellIndexList):
        locTypes  = [0 for x in range(self.numLocTypes)]

        for (cellX, cellY) in cellIndexList: 
            tmpLocTypes = self.grid.get( (cellX,cellY), [0 for x in range(self.numLocTypes)])
            locTypes = self.mergeLocTypes( locTypes, tmpLocTypes)

        return locTypes

    #######################################################
    def mergeLocTypes( self, locTypes, tmpLocTypes):
        locTypes = [ x + tmpLocTypes[i] for i,x in enumerate(locTypes)]
        return locTypes

    #######################################################
    def isVulnerable(self, cellIndexList):
        locTypes = self.getLocTypes(cellIndexList)
        numZeros = locTypes.count(0)
        if numZeros == self.numLocTypes-1:
            return True # vulnerable
        return False # not vulnerable

    #######################################################
    def __loadNodeinfo( self, nodeinfoFilename):
        fstr = open(nodeinfoFilename).read()
        clusteredStayPoints = {}

        nodeinfoDict = {}
        locTypes = []

        for line in fstr.split("\n"):
            if line == "":
                continue

            items = line.split("\t")

            spIndex = int(items[0])
            x = float(items[1].split(",")[0])
            y = float(items[1].split(",")[1])
            locType = int(items[3])
            nodeinfoDict[(x,y)] = locType
            locTypes.append(locType)

            clusteredStayPoints[locType] = clusteredStayPoints.get(locType, [])
            clusteredStayPoints[locType].append( (x,y))

        self.numLocTypes = max(locTypes) + 1

        self.clusteredStayPoints = []
        for i in range(self.numLocTypes):
            self.clusteredStayPoints.append( clusteredStayPoints[i])
        return  nodeinfoDict

#################################################################
if __name__ == "__main__":
    #attack = Attack( logDir = "./log/jung/", gridSize = GRID_SIZE )
    #attack = Attack( logDir = "./log/rich/", gridSize = GRID_SIZE )
    
    attack = Attack( logDir = "./log/rainbow/", gridSize = 100)
    print attack.typeDistanceMat
    print attack.isVulnerable( [(1,2),(3,4),(5,6)])
    print attack.computeEMD( [(1,2),(3,4),(5,6)])

