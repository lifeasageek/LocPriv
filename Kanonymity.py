#!/usr/bin/python

import random
import Attack
import sys
import option

#GRID_SIZE = 50
#MAX_NUM_LOOPS = 150
#SKIP_FOLLOW = 500
#MAX_NUM_ID = 200

#######################################################
class Grid:
    #######################################################
    def __init__(self, logDir, gridSize):
        self.gridSize = gridSize

        #(x_min, x_max, y_min, y_max)= self.getMapRanges( logDir + "/log.txt") 
        #self.xRange = ((int(x_min)/self.gridSize)*self.gridSize, (int(x_max)/self.gridSize+1)*self.gridSize)
        #self.yRange = ((int(y_min)/self.gridSize)*self.gridSize, (int(y_max)/self.gridSize+1)*self.gridSize)
        #print "xRange : ", self.xRange
        #print "yRange : ", self.yRange

        self.trajectory = self.loadLogfile(logDir + "/log.txt")
        self.grid = self.createGrid(self.trajectory)
        return

    #######################################################
    def getCellIndex( self, (x, y)):
        return (self.adjValue(x), self.adjValue(y))

    #######################################################
    def computeNumUsers( self, cellIndexList, ts):
        numUsers = 0
        for (cellX,cellY) in cellIndexList:
            #numUsers = numUsers + self.grid.get( (cellX,cellY), 0)

            if self.grid.get( (cellX, cellY), None) != None:
                numUsers = numUsers + self.grid[(cellX, cellY)].get(ts, 0)
        return numUsers

    #######################################################
    def extendCell_numUsers( self, cellIndexList, ts):
        direction = random.sample( ['N','E','S','W'], 1)[0]

        # choose the direction based on the kanonymity value
        # if it is all the same, simply return random direction

        maxNumUsers = 0
        for tmpDirection in ['N','E','S','W']:
            tmpCellIndexList = self.__extendCell(cellIndexList, tmpDirection)
            tmpNumUsers = self.computeNumUsers( tmpCellIndexList, ts)
            #print tmpDirection, tmpNumUsers

            if tmpNumUsers > maxNumUsers:
                maxNumUsers = tmpNumUsers
                direction = tmpDirection
        #print "CHOOSED : ", direction

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
    def createGrid( self, trajectory):
        print "createGrid()"

        grid = {}
        for nodeid, trajs in trajectory.iteritems():
            for (x,y,ts) in trajs:
                adjX = self.adjValue(x)
                adjY = self.adjValue(y)

                #grid[(adjX, adjY)] = grid.get( (adjX,adjY), 0)
                #grid[(adjX, adjY)] = grid[(adjX, adjY)] + 1

                grid[(adjX, adjY)] = grid.get( (adjX, adjY), {})
                grid[(adjX, adjY)][ts] = grid[(adjX, adjY)].get( ts, 0)
                grid[(adjX, adjY)][ts] = grid[(adjX, adjY)][ts] + 1

        return grid

    #######################################################
    def getMapRanges( self, logFilename):
        print "getMapRanges()"

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

        return (x_min, x_max, y_min, y_max)


    #######################################################
    def loadLogfile( self, logFilename):
        print "loadLogfile()"
        trajectory = {}

        fstr = open(logFilename).read()

        maxNodeId = -1
        for line in fstr.split("\n"):
            if line == "": # EOF
                break
            items = line.split("\t")

            nodeid = int(items[1])
            maxNodeId = max( nodeid, maxNodeId)

            x = float(items[5])
            y = float(items[6])
            time = int(items[4])

            try:
                trajectory[nodeid].append( (x, y, time))
            except:
                trajectory[nodeid] = []
                trajectory[nodeid].append( (x, y, time))
        return trajectory

#################################################################
class Kanonymity:
    #################################################################
    def __init__(self, logDir, k_threshold ):
        self.gridSize = option.getGridSize()
        self.maxNumLoops = option.getMaxNumLoops()
        self.skipFollow = option.getSkipFollow()
        self.maxNumId = option.getMaxNumId()

        self.k_threshold = k_threshold
        self.grid = Grid( logDir, self.gridSize )
        self.logDir = logDir

        self.attack = Attack.Attack( logDir = self.logDir, gridSize = self.gridSize)

        self.followEachUser()
        self.dumpResult( logDir + "/kanonymity")
        return

    #################################################################
    def followEachUser(self):
        print "followEachUser()"

        self.numOfQuery = 0
        self.numOfVulnerableQuery = 0

        self.sumKanomValues= 0 
        self.sumQueryCellSize = 0
        self.sumOrgEmdValue = 0
        self.numFailed = 0
        self.allOrgEmdValues = []

        numId = 0
        for nodeid, trajs in self.grid.trajectory.iteritems():
            numId = numId + 1
            if numId > self.maxNumId:
                break

            print "nodeid : ", nodeid

            for i, (x,y,timeStamp) in enumerate(trajs):
                if i % self.skipFollow != 1:
                    continue
                self.numOfQuery = self.numOfQuery + 1
                (kAnomValue, cellIndexList, isFailed) = self.computeCloakArea(x, y, timeStamp)
                #print kAnomValues, len(cellIndexList), kAnomValues

                self.sumKanomValues= self.sumKanomValues + kAnomValue
                self.sumQueryCellSize = self.sumQueryCellSize + len(cellIndexList)

                if sum(self.attack.getLocTypes(cellIndexList)) == 0:
                    self.numFailed = self.numFailed + 1

                orgEmdValue = self.attack.computeEMD(cellIndexList)
                self.sumOrgEmdValue = self.sumOrgEmdValue + orgEmdValue
                self.allOrgEmdValues.append((orgEmdValue, isFailed, len(cellIndexList)))

                if self.attack.isVulnerable(cellIndexList) == True:
                    self.numOfVulnerableQuery = self.numOfVulnerableQuery + 1

            #break
        return

    #################################################################
    def computeCloakArea(self, x, y, ts ):

        cellIndex  = self.grid.getCellIndex( (x, y))
        cellIndexList = [cellIndex]

        kAnomValues = []
        cellIndexLists = []

        isFailed = True
        for i in range(self.maxNumLoops):
            cellIndexList = self.grid.extendCell_numUsers( cellIndexList, ts) 

            kAnomValue = self.grid.computeNumUsers( cellIndexList, ts)

            kAnomValues.append(kAnomValue)
            cellIndexLists.append(cellIndexList)

            if kAnomValue >= self.k_threshold:
                isFailed = False
                return (kAnomValue, cellIndexList, isFailed)

        # if fails, then goes back to the cellIndexList which has the maximum lDivValues
        index = kAnomValues.index( max(kAnomValues))
        cellIndexList = cellIndexLists[index]
        return (kAnomValue, cellIndexList, isFailed)

    #######################################################
    def dumpResult( self, dumpFilename):
        print "dumpResult()"
        f = open(dumpFilename + "_stat_%d.txt" % (self.k_threshold), "w")

        f.write("logDir: " + self.logDir + "\n")
        f.write("gridSize : " + str(self.gridSize) + "\n")
        f.write("MAX_NUM_LOOPS: " + str(self.maxNumLoops) + "\n" )
        f.write("self.k_threshold: "+ str(self.k_threshold) + "\n\n" )

        f.write("numOfQuery: " + str(self.numOfQuery) + "\n")
        f.write("numOfVulnerableQuery :" + str(self.numOfVulnerableQuery) + "\n\n" )

        f.write("sumKanomValues: " + str(self.sumKanomValues) + "\n" )
        f.write("sumQueryCellSize: " + str(self.sumQueryCellSize) + "\n" )
        f.write("sumOrgEmdValue: " + str(self.sumOrgEmdValue) + "\n" )
        f.write("numFailed: " + str(self.numFailed) + "\n" )
        f.write("avgOrgEmd: " + str(self.sumOrgEmdValue / (self.numOfQuery - self.numFailed)) + "\n" )
        f.close()

        f = open(dumpFilename + "_orgEmdValues_%d.txt" % (self.k_threshold), "w")
        for emdValue, isFailed, cellSize in self.allOrgEmdValues:
            f.write("%lf %s %d\n" % (emdValue, (str(isFailed)), cellSize))
        f.close()
        print "end of dumpResult()"
        return

#################################################################
if __name__ == "__main__":
    #logDir = "./log/jung/"
    #logDir = "./log/rainbow/"
    logDir = option.getLogDir()

    k_threshold = 3

    if len(sys.argv)  > 1:
        k_threshold = int(sys.argv[1])

    print "k_threshold : ", k_threshold
    Kanonymity = Kanonymity( logDir = logDir, k_threshold = k_threshold)

