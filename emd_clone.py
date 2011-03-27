#!/usr/bin/python

from ctypes import *

MAX_NUM_TYPES = 100

Features = c_int * MAX_NUM_TYPES
Weights = c_float * MAX_NUM_TYPES
Distances = c_float * (MAX_NUM_TYPES * MAX_NUM_TYPES)

class Signatures(Structure):
    _fields_ = [
            ("n", c_int),
            ("Features",POINTER(Features)),
            ("Weights",POINTER(Weights))
            ]

class EMD:
    def __init__(self):
        self.emd_module = cdll.LoadLibrary("./emd_clone/emd.so")

        self.emd_module.emd_staypoint.restype = c_float
        self.emd_module.emd_type.restype = c_float

        self.w1 = Weights()
        self.w2 = Weights()

        self.f1 = Features()
        self.f2 = Features()
        return

    def setFeatures(self, features):
        self.length = len(features)

        maxDistValue = features[-1] - features[0]
        self.emd_module.setMaxDistValue(c_float(maxDistValue))

        for i, value in enumerate(features):
            self.f1[i] = value
            self.f2[i] = value
        return

    def __setWeight( self, w1, w2):
        if self.length != len(w1) or self.length != len(w2):
            print "WARNING : EMD feature length is different"
        for i, value in enumerate(w1):
            self.w1[i] = value

        for i, value in enumerate(w2):
            self.w2[i] = value
        return

    def __setSignature( self):
        self.s1 = Signatures( self.length, pointer(self.f1), pointer(self.w1))
        self.s2 = Signatures( self.length, pointer(self.f2), pointer(self.w2))
        return

    def computeStaypoint(self, w1, w2):
        self.__setWeight(w1, w2)
        self.__setSignature()

        e = self.emd_module.emd_staypoint( byref(self.s1), byref(self.s2))
        return e

    def setTypeDistanceMat(self, distances ):
        self.distances = Distances()
        for i, d in enumerate(distances):
            self.distances[i] = d

        self.emd_module.setTypeDistanceMat( c_int(self.length), byref(self.distances))
        return

    def computeType(self, w1, w2):
        self.__setWeight(w1, w2)
        self.__setSignature()

        e = self.emd_module.emd_type( byref(self.s1), byref(self.s2))
        return e
    
def testStayPoint():
    emd = EMD()
    emd.setFeatures( [0,20,40,60,80])
    e = emd.computeStaypoint( [0.2,0.2,0.2,0.2, 0.2], [0.2,0.2,0.2,0.2,0.2])
    print "emd testStayPoint : ", e
    e = emd.computeStaypoint( [0.2,0.2,0.2,0.2, 0.2], [0.1,0.2,0.2,0.2,0.3])
    print "emd testStayPoint : ", e
    return

def testType():
    emd = EMD()
    emd.setFeatures( [0,1,2])
    emd.setTypeDistanceMat( [0,0.5,0.2,0.4,0,0.8,0.1,0.1,0] )
    e = emd.computeType( [0.3,0.4,0.3], [0.3,0.5,0.2])
    print "emd testType: ", e
    return 

if __name__ == "__main__":
    testStayPoint()
    testType()

