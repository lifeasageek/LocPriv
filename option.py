#!/usr/bin/python

LOG_DIR = "./log/boa/"
GRID_SIZE = 140
MAX_NUM_LOOPS = 100
SKIP_FOLLOW = 500
MAX_NUM_ID = 1000

def getGridSize():
    return GRID_SIZE

def getMaxNumLoops():
    return MAX_NUM_LOOPS

def getSkipFollow():
    return SKIP_FOLLOW

def getMaxNumId():
    return MAX_NUM_ID

def getLogDir():
    return LOG_DIR

if __name__ == "__main__":
    getLogDir()
    getGridSize()
    getMaxNumLoops()
    getSkipFollow()
    getMaxNumId()

