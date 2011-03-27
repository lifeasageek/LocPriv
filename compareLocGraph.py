#!/usr/bin/python

import emd
import pickle
import Attack
import numpy

import option

class LocSemGraph:
    #######################################################
    def __init__(self, logDir):
        self.loadClusteredStayPoints( logDir)
        self.initEMD()
        return

    #################################################################
    def initEMD(self):
        self.univLocTypesPDF = self.computePDF([len(x) for x in self.clusteredStayPoints])

        self.emd_module = emd.EMD()
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
    def computePDF(self, locTypes):
        totalNum = sum(locTypes)
        if totalNum == 0:
            totalNum = 1
        return [ x*1.0/totalNum for x in locTypes]

    #################################################################
    def computeEMD(self, locTypes):

        locTypesPDF = self.computePDF( locTypes)

        #print "locTypesPDF : ", locTypesPDF
        #print "univLocTypesPDF :", self.univLocTypesPDF

        emdValue = self.emd_module.computeType( locTypesPDF, self.univLocTypesPDF)
        #print "emd : ", emdValue
        return emdValue



    #######################################################
    def loadClusteredStayPoints( self, logDir):
        print "loadClusteredStayPoints()"

        pkl_file = open( logDir + './mining.pkl', 'rb')

        self.clusteredStayPoints = pickle.load( pkl_file)
        self.typeDuration = pickle.load( pkl_file)
        self.typeDistanceMat = pickle.load( pkl_file)
        print "-"*20
        self.numLocTypes = len(self.clusteredStayPoints)
        print "-"*20

        print self.typeDistanceMat

        pkl_file.close()
        return


#######################################################
def compare(actual, learn):
    sumDiff = 0
    #sumDiffProp = 0
    for i in range(len(actual)):
        for j in range(len(actual)):
            if j>=i:
                continue
            #print  actual[i][j],learn[i][j]
            sumDiff = sumDiff + abs(actual[i][j] - learn[i][j])
            #sumDiffProp = sumDiffProp + abs(actual[i][j] - learn[i][j]) / actual[i][j]

    totalSize = len(actual) * (len(actual)-1) / 2
    normDiff = sumDiff/totalSize

    #print "totalSize : ", totalSize
    #print "sumDiff :", sumDiff
    #print "sumDiff/len :", normDiff
    #print "sumDiffProp : ", sumDiffProp / 16.0

    return normDiff

#######################################################
def createRandomMat( size):
    mat = numpy.zeros((size,size))

    for i in range(size):
        for j in range(size):
            if j>=i:
                continue
            value = numpy.random.uniform(0,1)
            mat[i][j] = value
    #print mat
    return mat

#######################################################
def randomCompare(actualLSG):
    size = len(actualLSG)
    sumDiff = 0.0
    for i in range(30):
        randMat = createRandomMat( size)
        diff = compare(actualLSG, randMat)
        sumDiff = sumDiff + diff
        print diff
    avgDiff = sumDiff / 30
    print "avgDiff : ", avgDiff
    return avgDiff

#######################################################
def transform( learnLSG, seqList):
    newLSG = numpy.ndarray((len(learnLSG), len(learnLSG)))

    for i in range(len(learnLSG)):
        for j in range(len(learnLSG)):
            print i, j, learnLSG[i][j]
            newLSG[ seqList[i]][seqList[j]] = learnLSG[i][j]

    print newLSG 
    return newLSG



#######################################################
if __name__ == "__main__":
    #logDir = "./log/rainbow/"
    logDir = option.getLogDir()
    learn = LocSemGraph( logDir)
    learnLSG = learn.typeDistanceMat
    actual = Attack.Attack( logDir = logDir, gridSize = 100)
    actualLSG = actual.typeDistanceMat


    print type(learnLSG)
    print "---learn---"
    print learnLSG
    print "---actual---"
    print actualLSG

    #learnLSG = transform( learnLSG, [3,1,2,0])
    learnLSG = transform( learnLSG, [2,1,3,0])

    D_ML = compare( actualLSG, learnLSG)
    print "D_ML : ", D_ML

    D_MR = randomCompare(actualLSG )
    print "D_MR : ", D_MR
