#!/usr/bin/python

import Grid
import Attack
import sys
import emd
import option


#METHOD = "random"
METHOD = "emd"
#METHOD = "loc"

#################################################################
class Closeness:
    #################################################################
    def __init__(self, logDir, emd_thresold ):
        self.gridSize = option.getGridSize()
        self.maxNumLoops = option.getMaxNumLoops()
        self.skipFollow = option.getSkipFollow()
        self.maxNumId = option.getMaxNumId()



        self.logDir = logDir
        self.emd_thresold = emd_thresold

        self.attack = Attack.Attack( logDir = self.logDir, gridSize = self.gridSize)

        self.grid = Grid.Grid( logDir, self.gridSize )
        self.numLocTypes = self.grid.getNumLocTypes()

        print "numLocTypes : ", self.numLocTypes
        print "numStayPoints : ", sum( [len(x) for x in self.grid.clusteredStayPoints])
        self.followEachUser()

        self.dumpResult( logDir + "/closeness")

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


    #################################################################
    def computeCloakArea(self, x, y ):

        cellIndex  = self.grid.getCellIndex( (x, y))

        cellIndexList = [cellIndex]
        #print cellIndexList

        isFailed = True
        emdValues = []
        cellIndexLists = []

        for i in range(self.maxNumLoops):
            #print "-" * 20
            if METHOD == "random":
                cellIndexList = self.grid.extendCell_random( cellIndexList) # TODO
            elif METHOD == "loc":
                cellIndexList = self.grid.extendCell_maxNumLoc( cellIndexList) # TODO
            elif METHOD == "emd":
                cellIndexList = self.grid.extendCell_minEMD( cellIndexList) # TODO
            else:
                "ERROR!!"

            thisLocTypes = self.grid.getLocTypes( cellIndexList)

            #print "thisLocTypes : ", thisLocTypes
            emdValue = self.grid.computeEMD( thisLocTypes)

            emdValues.append(emdValue)
            cellIndexLists.append(cellIndexList)

            if emdValue <= self.emd_thresold:
                isFailed = False
                return (emdValue, cellIndexList, isFailed)

        # if fails, then goes back to the cellIndexList which has the smallest emdValue
        index = emdValues.index( min(emdValues))
        cellIndexList = cellIndexLists[index]
        return (emdValue, cellIndexList, isFailed)

    #################################################################
    def followEachUser(self):
        print "followOneUser()"

        self.numOfQuery = 0
        self.numOfVulnerableQuery = 0

        self.sumEMDValues = 0 
        self.sumQueryCellSize = 0

        self.sumOrgEmdValue = 0
        self.numNoLocTypes = 0

        # follow up one user
        trajectory = self.getTrajectoryFromLogfile()
        self.allObtainedEMDValues = []
        self.allOrgEmdValues = []

        numId = 0
        for nodeid, traj in trajectory.iteritems():
            numId = numId + 1
            if numId > self.maxNumId:
                break


            print "nodeid : ", nodeid

            for i, (x,y,time) in enumerate(traj):
                if i % self.skipFollow != 1:
                    continue

                self.numOfQuery = self.numOfQuery + 1
                (emdValue, cellIndexList, isFailed) = self.computeCloakArea( x, y)

                self.allObtainedEMDValues.append((emdValue, isFailed, len(cellIndexList)))

                self.sumEMDValues = self.sumEMDValues + emdValue
                self.sumQueryCellSize = self.sumQueryCellSize + len(cellIndexList)

                if sum(self.attack.getLocTypes(cellIndexList)) == 0:
                    self.numNoLocTypes = self.numNoLocTypes + 1

                orgEmdValue = self.attack.computeEMD(cellIndexList)
                self.sumOrgEmdValue = self.sumOrgEmdValue + orgEmdValue
                self.allOrgEmdValues.append((orgEmdValue, isFailed, len(cellIndexList)))

                if self.attack.isVulnerable(cellIndexList) == True:
                    #print "VULERNABLE"
                    self.numOfVulnerableQuery = self.numOfVulnerableQuery + 1
        return

    #######################################################
    def getTrajectoryFromLogfile( self):
        print "getTrajectoryFromLogfile()"

        logFilename = self.logDir + "/log.txt"

        fstr = open(logFilename).read()
        trajectory = {}

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

    #######################################################
    def dumpResult( self, dumpFilename):
        print "dumpResult()"
        f = open(dumpFilename + "_stat_%lf.txt" % (self.emd_thresold), "w")

        f.write("logDir: " + self.logDir + "\n")
        f.write("gridSize : " + str(self.gridSize) + "\n")
        f.write("MAX_NUM_LOOPS: " + str(self.maxNumLoops) + "\n" )
        f.write("EMD_THRESHOLD: "+ str(self.emd_thresold) + "\n\n" )
        f.write("METHOD: "+ METHOD + "\n\n" )

        f.write("numOfQuery: " + str(self.numOfQuery) + "\n")
        f.write("numOfVulnerableQuery :" + str(self.numOfVulnerableQuery) + "\n" )
        f.write("sumEMDValues: " + str(self.sumEMDValues) + "\n\n" )

        f.write("sumQueryCellSize: " + str(self.sumQueryCellSize) + "\n" )
        f.write("sumOrgEmdValue: " + str(self.sumOrgEmdValue) + "\n" )
        f.write("numNoLocTypes: " + str(self.numNoLocTypes) + "\n" )
        f.write("avgOrgEmd: " + str(self.sumOrgEmdValue / (self.numOfQuery - self.numNoLocTypes)) + "\n" )

        f.close()

        f = open(dumpFilename + "_orgEmdValues_%lf.txt" % (self.emd_thresold), "w")
        for emdValue, isFailed, cellSize in self.allOrgEmdValues:
            f.write("%lf %s %d\n" % (emdValue, (str(isFailed)), cellSize))
        f.close()

        f = open(dumpFilename + "_obtainedEmdValues_%lf.txt" % (self.emd_thresold), "w")
        for emdValue, isFailed, cellSize in self.allObtainedEMDValues:
            f.write("%lf %s %d\n" % (emdValue, (str(isFailed)), cellSize))
        f.close()
        return



#################################################################
if __name__ == "__main__":
    #logDir = "./log/rich/"
    #logDir = "./log/secret/"
    #logDir = "./log/missa/"
    #logDir = "./log/rainbow/"

    logDir = option.getLogDir()
    emd_thresold = 0.05

    if len(sys.argv)  > 1:
        emd_thresold = float(sys.argv[1])

    print "emd_thresold : ", emd_thresold
    closeness = Closeness( logDir = logDir, emd_thresold = emd_thresold )
    print "END of Closeness"

