#!/usr/bin/python
"""
miningStayPoint.py

- Author : Byoungyoung Lee

2010/07/20 - the frequency of visits onto each stay point is obtained 
2010/07/20 - mining stay points from trajectories
"""
import scipy
import pylab
import numpy
import scipy.cluster.hierarchy as sch
import pickle

import emd
import option

THRESHOLD_DIST = 5
NUM_TRAJS = 20

NUM_LOC_TYPES = 4

MAX_TIME = 500
BIN_SIZE = 10

#######################################################
class ManageStayPoints:
    #######################################################
    def __init__(self, logDir):
        Traj = self.loadLogfile( logDir + "/log.txt") 
        self.logStr = ""

        ######################################################
        ## mining stay points
        ######################################################
        StayPoints = self.miningStayPoint( Traj)

        while 1:
            if self.cleaningStayPoint( StayPoints) == False:
                break

        stayDuration = self.computeStayDuration( Traj, StayPoints )
        #clusteredStayPoints = self.clusteringStayPoint(stayDuration)
        clusteredStayPoints = self.kmeansClustering(stayDuration)

        self.evaluate( StayPoints, clusteredStayPoints, logDir + '/nodeinfo.txt')

        typeDuration = self.computeTypeDuration( clusteredStayPoints, stayDuration)
        typeDistanceMat = self.computeTypeDistanceMat(typeDuration)
        print typeDistanceMat
        self.saveResult(logDir, clusteredStayPoints, typeDuration, typeDistanceMat)
        print "numStayPoints from cluster: ", sum( [len(x) for x in clusteredStayPoints])
        return

    #######################################################
    def saveResult( self, logDir, clusteredStayPoints, typeDuration, typeDistanceMat):
        output = open( logDir + './mining.pkl', 'wb')

        pickle.dump( clusteredStayPoints, output)
        pickle.dump( typeDuration, output)
        pickle.dump( typeDistanceMat, output)

        output.close()
        return

    #######################################################
    def computeTypeDuration( self, clusteredStayPoints, stayDuration):

        typeDuration = []
        for cluster in clusteredStayPoints:
            durationDistr = {}
            for (x,y) in cluster:
                tmpDurationDistr = stayDuration[(x,y)]
                for duration, freq in tmpDurationDistr.iteritems():
                    durationDistr[duration] = durationDistr.get(duration,0) + freq
            typeDuration.append(durationDistr)

        return typeDuration

    #######################################################
    def evaluate( self, stayPointList, clusteredStayPoints, nodeinfoFilename):
        nodeinfoDict = self.loadNodeinfo(nodeinfoFilename)

        # number of stay points
        self.evaluateStayPoints( stayPointList, nodeinfoDict)

        # number of location types
        orgLocTypeSize = len(set(nodeinfoDict.values()))
        minedLocTypeSize = len(clusteredStayPoints)

        print "minedLocTypeSize : ", minedLocTypeSize
        print "orgLocTypeSize : ", orgLocTypeSize

        # clustering accuracy
        self.evaluateClustering(clusteredStayPoints, nodeinfoDict)
        return

    #######################################################
    def evaluateClustering(self, clusteredStayPoints, nodeinfoDict):
        for i, cluster in enumerate(clusteredStayPoints):
            thisOrgLocTypes= []
            for (x1,y1) in cluster:
                minDist = 1000000
                minLoc = None

                # find closest one
                for (x2,y2) in nodeinfoDict.keys():
                    dist = (x1 - x2)**2 + (y1 - y2)**2

                    if dist < minDist:
                        minDist = dist
                        minLoc = (x2,y2)
                thisOrgLocTypes.append( nodeinfoDict[minLoc])
            print thisOrgLocTypes

        return

    #######################################################
    def computeDistanceMatrix( self, stayDuration):
        print "computeDistanceMatrix()"
        num = len(stayDuration)
        D = scipy.zeros( [num,num])

        for i, ((x1,y1), duration1) in enumerate(stayDuration.iteritems()):
            for j, ((x2,y2), duration2) in enumerate(stayDuration.iteritems()):
                #distance = self.computeKLDistance( duration1, duration2)
                distance = self.computeEMD( duration1, duration2)
                #distance = computeJaccardDistance( distr1, distr2)
                D[i,j] = distance
        return D

    #################################################################
    def computeTypeDistanceMat(self, typeDuration):
        print "computeTypeDistanceMat()"

        print "len(typeDuration) : ", len(typeDuration)

        D = scipy.zeros( [len(typeDuration),len(typeDuration)])

        for i, (duration1) in enumerate(typeDuration):
            print duration1
            for j, ( duration2) in enumerate(typeDuration):
                distance = self.computeEMD( duration1, duration2)
                D[i,j] = distance
        return D

    #######################################################
    def computeEMD( self, distr1, distr2):
        emd_module = emd.EMD()
        feature = range(0,MAX_TIME, BIN_SIZE)
        emd_module.setFeatures( feature)

        w1 = [0 for x in range(0,MAX_TIME, BIN_SIZE)]
        w2 = [0 for x in range(0,MAX_TIME, BIN_SIZE)]

        sum1 = sum(distr1.values())
        sum2 = sum(distr2.values())

        for duration, freq in distr1.iteritems():
            w1[duration/BIN_SIZE] = freq*1.0 / sum1

        for duration, freq in distr2.iteritems():
            w2[duration/BIN_SIZE] = freq*1.0 / sum2
        e = emd_module.computeStaypoint(w1,w2)

        return e

    #######################################################
    def computeKLDistance( self, distr1, distr2):
        sumDistr1 = sum(distr1.values())
        sumDistr2 = sum(distr2.values())

        kl_dist = 0.0
        for nodeid in distr1.keys():
            px = 1.0 * distr1[nodeid] / sumDistr1
            qx = 1.0 * distr2.get(nodeid,0.0001) / sumDistr2

            #if qx == 0: # TODO
            #    continue

            kl_dist = kl_dist + px * numpy.log(qx/px)
        kl_dist = numpy.abs(kl_dist)
        return kl_dist

    #######################################################
    def kmeansClustering( self, stayDuration):
        print "kmeansClustering()"

        K = NUM_LOC_TYPES

        # select first K points as initial distrs
        clusterDistr = {}
        for i, ((x1,y1), duration) in enumerate(stayDuration.iteritems()):
            if i >= K:
                break
            clusterDistr[i] = duration

        
        for i in range(30):
            print "K-means clustering LOOP %d" % i
            # assign each point to the closest cluster
            clusters = {}
            for k in range(K):
                clusters[k] = []

            for i, ((x,y), duration1) in enumerate(stayDuration.iteritems()):
                dists = []
                for (j, duration2) in clusterDistr.iteritems():
                    dist = self.computeEMD( duration1, duration2)
                    dists.append(dist)

                k = dists.index(min(dists))
                clusters[k].append( ((x,y), duration1))


            clusterDistr = {}
            # recompute the distribution of each cluster
            for k, durations in clusters.iteritems():
                clusterDistr[k] = {}
                for (x,y), duration in durations:
                    clusterDistr[k] = self.mergeStayPointDistrs( clusterDistr[k], duration)


        # return clustering results
        clusteredStayPoints = []
        for k, durations in clusters.iteritems():
            thisCluster = []
            for (x,y), duration in durations:
                thisCluster.append((x,y))
            clusteredStayPoints.append(thisCluster)
        return clusteredStayPoints

    #######################################################
    def clusteringStayPoint( self, stayDuration, method='single'):
        print "clusteringStayPoint()"

        D = self.computeDistanceMatrix( stayDuration)

        pylab.figure()

        Y = sch.linkage(D, method)

        clusteredStayPoints = []

        # initialize clusteredStayPoints
        for i, ((x1,y1), duration1) in enumerate(stayDuration.iteritems()):
            print i, x1, y1
            clusteredStayPoints.append( ([(x1,y1)], True))

        numMerged = 0
        for [nodeLeftIndex, nodeRightIndex, closeness, step] in Y:
            (leftNodeList, isLeftVisisted) = clusteredStayPoints[int(nodeLeftIndex)]
            (rightNodeList, isRightVisisted) = clusteredStayPoints[int(nodeRightIndex)]

            clusteredStayPoints[int(nodeLeftIndex)] = (leftNodeList, False)
            clusteredStayPoints[int(nodeRightIndex)] = (rightNodeList, False)

            leftNodeList.extend(rightNodeList) # merge two types
            clusteredStayPoints.append( (leftNodeList, True) ) # append merged types at the end

            numMerged = numMerged + 1

            if len(stayDuration) - numMerged <= NUM_LOC_TYPES:
                break
        
        # cleanup clusteredStayPoints
        tmpClusteredStayPoints = []
        for nodeList, isVisited in clusteredStayPoints:
            if isVisited == True:
                tmpClusteredStayPoints.append( nodeList)

        clusteredStayPoints = tmpClusteredStayPoints

        for nodeList in clusteredStayPoints:
            print nodeList


        Z1 = sch.dendrogram(Y, orientation='top')
        #pylab.show()
        pylab.savefig('%s.png' % method)
        return clusteredStayPoints

    #######################################################
    def computeStayDuration( self, Traj, StayPoints):
        print "computeStayDuration()"
        print StayPoints

        stayDuration = {}

        for nodeid, trajs in Traj.iteritems():
            thisStayHistory = {}

            for i, (x,y,timeStamp) in enumerate(trajs):
                #closePoints = self.findClosePoints( (x,y), StayPoints)

                #for cx, cy in closePoints:
                    #thisStayHistory[(cx,cy)] = thisStayHistory.get((cx,cy),[])
                    #thisStayHistory[(cx,cy)].append(timeStamp)

                closePoint = self.findClosestPoint( (x,y), StayPoints)
                if closePoint != (-1,-1):
                    thisStayHistory[closePoint] = thisStayHistory.get(closePoint,[])
                    thisStayHistory[closePoint].append(timeStamp)

            timeStamps = reduce(lambda x, y: x.union(y), map(set, thisStayHistory.values()))
            maxTimeStamp = max(timeStamps)

            toDelete = (-1,-1)
            for (cx,cy), timeStamps in thisStayHistory.iteritems():
                #print "timeStamps :", timeStamps
                try:
                    timeStamps.index(maxTimeStamp)
                    toDelete = (cx,cy)
                except:
                    pass

            if toDelete != (-1,-1):
                thisStayHistory[toDelete] = []


            for (cx, cy), timeStamps in thisStayHistory.iteritems():
                duration = 1
                for i in range(len(timeStamps)-1):
                    curTimeStamp = timeStamps[i]
                    nextTimeStamp = timeStamps[i+1]

                    if nextTimeStamp - curTimeStamp == 1 and i < len(timeStamps)-2:
                        duration = duration + 1
                    else:
                        if duration <  NUM_TRAJS:
                            duration = 1
                        else:
                            stayDuration[(cx,cy)] = stayDuration.get((cx,cy),{})
                            duration = int(duration) / BIN_SIZE
                            duration = int(duration) * BIN_SIZE
                            stayDuration[(cx,cy)][duration] = stayDuration[(cx,cy)].get(duration, 0) + 1
                            duration = 1

        return stayDuration

    #######################################################
    def loadLogfile( self, logFilename):
        print "loadLogfile()"
        Traj = {}

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
                Traj[nodeid].append( (x, y, time))
            except:
                Traj[nodeid] = []
                Traj[nodeid].append( (x, y, time))
        return Traj

    #######################################################
    def findClosePoints( self, (x,y), points):
        closePoints = []
        for (px,py) in points:
            dist = (x - px)**2 + (y - py)**2
            if dist <= THRESHOLD_DIST: 
                closePoints.append(( px,py))

        return closePoints

    #######################################################
    def findClosestPoint( self, (x,y), points):
        closePoint = (-1,-1)
        min_dist = 100000000
        for (px,py) in points:
            dist = (x - px)**2 + (y - py)**2
            if dist < min_dist and dist <= THRESHOLD_DIST:
                min_dist = dist
                closePoint = (px,py)

        return closePoint



    #######################################################
    def isClose( self, xs, ys):
        avg_x = sum(xs)/len(xs)
        avg_y = sum(ys)/len(ys)

        for i in range(len(xs)):
            dist = (xs[i] - avg_x)**2 + (ys[i] - avg_y)**2
            if dist > THRESHOLD_DIST: 
                return False
        return True

    #######################################################
    def miningStayPoint( self, Traj):
        print "miningStayPoint()"
        """
        mining stay points from trajectories
        recording visit frequencies as well
        """

        StayPoints = []
        for nodeid, trajs in Traj.iteritems():
            xs = []
            ys = []
            for i, traj in enumerate(trajs):
                x = traj[0]
                y = traj[1]
                xs.append(x)
                ys.append(y)

                if i < NUM_TRAJS: # initialize step, do not count this !
                    continue

                elif i >= NUM_TRAJS:
                    xs.pop(0)
                    ys.pop(0)

                if self.isClose( xs, ys) == True:
                    avg_x = sum(xs)/len(xs)
                    avg_y = sum(ys)/len(ys)

                    #med_index = NUM_TRAJS / 2
                    #avg_x = xs[med_index]
                    #avg_y = ys[med_index]

                    try:
                        StayPoints.index((avg_x, avg_y))
                    except:
                        StayPoints.append((avg_x, avg_y))

        return StayPoints
                
    #######################################################
    def mergeStayPointDistrs( self, freq1, freq2):
        newStayPointDistrs = {}

        for nodeid in set(freq1.keys()).union(set(freq2.keys())):
            cnt1 = freq1.get(nodeid,0)
            cnt2 = freq2.get(nodeid,0)
            newStayPointDistrs[nodeid] = cnt1+cnt2


        return newStayPointDistrs
    #######################################################
    def cleaningStayPoint( self, StayPoints):
        """
        if two stay points are too close, remove one of them
        """

        for i in range(len(StayPoints)):
            x1, y1 = StayPoints[i]
            for j in range(len(StayPoints)):
                if i>=j:
                    continue
                x2, y2 = StayPoints[j]
                dist = (x1 - x2)**2 + (y1 - y2)**2
                if dist < THRESHOLD_DIST:
                    # merge this ! 
                    avg_x = (x1+x2)/2
                    avg_y = (y1+y2)/2

                    StayPoints.remove((x1,y1))
                    StayPoints.remove((x2,y2))
                    StayPoints.append( (avg_x,avg_y))
                    return True
        return False

    #######################################################
    def loadNodeinfo( self, nodeinfoFilename):
        fstr = open(nodeinfoFilename).read()

        nodeinfoDict = {}

        for line in fstr.split("\n"):
            if line == "":
                continue

            items = line.split("\t")

            spIndex = int(items[0])
            x = float(items[1].split(",")[0])
            y = float(items[1].split(",")[1])
            locType = int(items[3])
            nodeinfoDict[(x,y)] = locType
        return  nodeinfoDict

    #######################################################
    def evaluateStayPoints( self, stayPointList, nodeinfoDict):
        print "Mined size : ", len(stayPointList)
        print "Original size: ", len(nodeinfoDict)

        # for each mined stay point, locate a nearest one and compute the distance from it
        sumMinError = 0
        for (x1,y1) in stayPointList:
            minError = -1
            for (x2,y2), locType in nodeinfoDict.iteritems():
                dist = (x1 - x2)**2 + (y1 - y2)**2
                #print "original :", x2,y2

                if minError == -1:
                    minError = dist
                if dist < minError:
                    minError = dist

            sumMinError = sumMinError + minError

        print "Sum of Minimum Error : ", sumMinError
        return

#######################################################
if __name__ == "__main__":
    #LOG_DIR = "../heavy2/"
    #LOG_DIR = "../log/simple/"
    #LOG_DIR = "../log/newsimple/"
    logDir = option.getLogDir()

    #manStayPoint = ManageStayPoints("./log/newsimple/")
    #manStayPoint = ManageStayPoints("./log/rich/")
    #manStayPoint = ManageStayPoints("./log/secret/")
    #manStayPoint = ManageStayPoints("./log/rainbow_test/")
    #manStayPoint = ManageStayPoints("./log/missa/")
    manStayPoint = ManageStayPoints(logDir)

