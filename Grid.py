#!/usr/bin/python

import pickle
import random
import emd
import gc

class Grid:
    #######################################################
    def __init__(self, logDir, gridSize ):

        self.gridSize = gridSize
        (x_min, x_max, y_min, y_max)= self.getMapRanges( logDir + "/log.txt") 
        self.xRange = ((int(x_min)/self.gridSize)*self.gridSize, (int(x_max)/self.gridSize+1)*self.gridSize)
        self.yRange = ((int(y_min)/self.gridSize)*self.gridSize, (int(y_max)/self.gridSize+1)*self.gridSize)

        print "xRange : ", self.xRange
        print "yRange : ", self.yRange

        self.loadClusteredStayPoints( logDir)
        self.initEMD()

        self.grid = self.createGrid()
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
    def getNumLocTypes( self):
        return self.numLocTypes

    #######################################################
    def getCellIndex( self, (x, y)):
        return (self.adjValue(x), self.adjValue(y))

    #######################################################
    def extendCell_minEMD( self, cellIndexList):
        direction = random.sample( ['N','E','S','W'], 1)[0]

        # choose the direction based on the EMD value of each direction
        # if it is all the same, simply return random direction
        minEMD = 100000 # TODO : what's the initial min Number??

        for tmpDirection in ['N','E','S','W']:
            tmpCellIndexList = self.__extendCell(cellIndexList, tmpDirection)
            tmpLocTypes = self.getLocTypes( tmpCellIndexList)
            tmpEMD = self.computeEMD(tmpLocTypes)
            #print tmpDirection, tmpEMD

            if tmpEMD < minEMD:
                minEMD = tmpEMD
                direction = tmpDirection  
        #print "CHOOSED :", direction

        return self.__extendCell( cellIndexList, direction)

    #######################################################
    def extendCell_maxNumLoc( self, cellIndexList):
        direction = random.sample( ['N','E','S','W'], 1)[0]

        # choose the direction based on the number of locations in each direction
        # if it is all the same, simply return random direction
        maxNumLocTypes = 0
        for tmpDirection in ['N','E','S','W']:
            tmpCellIndexList = self.__extendCell(cellIndexList, tmpDirection)
            tmpNumLocTypes = sum( self.getLocTypes( tmpCellIndexList))

            if tmpNumLocTypes > maxNumLocTypes:
                maxNumLocTypes = tmpNumLocTypes
                direction = tmpDirection

        return self.__extendCell( cellIndexList, direction)

    #######################################################
    def extendCell_random( self, cellIndexList):
        #for (cellX, cellY) in cellIndexList:
        #    pass

        direction = random.sample( ['N','E','S','W'], 1)[0]
        return self.__extendCell( cellIndexList, direction)

    #######################################################
    def __extendCell( self, cellIndexList, direction):
        newCellIndexList = list(cellIndexList)

        min_x = min([l[0] for l in cellIndexList])
        max_x = max([l[0] for l in cellIndexList])

        min_y = min([l[1] for l in cellIndexList])
        max_y = max([l[1] for l in cellIndexList])

        pivotCord = None
        rangeList = None

        if direction == 'E' or direction == 'W':
            if direction == 'E':
                pivotCord = max_x + 1
            elif direction == 'W':
                pivotCord = min_x - 1

            rangeList = range(min_y, max_y + 1)
            newCellIndexList.extend( [(pivotCord, l) for l in rangeList])

        elif direction == 'N' or direction == 'S':
            if direction == 'N':
                pivotCord = min_y - 1

            elif direction == 'S':
                pivotCord = max_y + 1
            rangeList = range(min_x, max_x+ 1)
            newCellIndexList.extend( [(l, pivotCord) for l in rangeList])

        return newCellIndexList

    #######################################################
    def adjValue( self, value):
        return int(value) / self.gridSize

    #######################################################
    def mergeLocTypes( self, locTypes, tmpLocTypes):
        locTypes = [ x + tmpLocTypes[i] for i,x in enumerate(locTypes)]
        return locTypes

    #######################################################
    def getLocTypes( self, cellIndexList):

        locTypes  = [0 for x in range(self.numLocTypes)]

        for (cellX, cellY) in cellIndexList: 
            tmpLocTypes = self.grid.get( (cellX,cellY), [0 for x in range(self.numLocTypes)])
            locTypes = self.mergeLocTypes( locTypes, tmpLocTypes)

        return locTypes

    #######################################################
    def createGrid( self):
        print "createGrid()"

        grid = {}

        for i, cluster in enumerate(self.clusteredStayPoints):
            for (x,y) in cluster:
                adjX = self.adjValue(x)
                adjY = self.adjValue(y)
                #print x, adjX
                #print y, adjY

                grid[(adjX, adjY)] = grid.get( (adjX,adjY), [0 for x in range(self.numLocTypes)])
                grid[(adjX, adjY)][i] = grid[(adjX, adjY)][i] + 1
        #print grid
        return grid

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
    def getMapRanges( self, logFilename):
        print "loadLogfile()"

        fstr = open(logFilename).read()

        xs = []
        ys = []
        for line in fstr.split("\n"):
            if line == "": # EOF
                break
            items = line.split("\t")

            x = float(items[5])
            y = float(items[6])
            xs.append(x)
            ys.append(y)
        x_min = min(xs)
        x_max = max(xs)
        y_min = min(ys)
        y_max = max(ys)
        print "end of loadLogfile()"

        return (x_min, x_max, y_min, y_max)

#######################################################
if __name__ == "__main__":
    grid = Grid( "./log/rich/", gridSize = 500 )
    grid = Grid( "./log/jung/", gridSize = 500 )
    #grid = Grid( "./log/hyori/", gridSize = 500 )
    
    cellIndex = grid.getCellIndex( (10003, 25004))
    cellIndexList = [cellIndex]
    print cellIndexList

    for i in range(10):
        #cellIndexList = grid.extendCell_random( cellIndexList)
        #cellIndexList = grid.extendCell_maxNumLoc( cellIndexList)
        cellIndexList = grid.extendCell_minEMD( cellIndexList)
        #print cellIndexList
        print grid.getLocTypes( cellIndexList)



