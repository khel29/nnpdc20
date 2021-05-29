import math
from math import *

def get_bearing(lat1, long1, lat2, long2):
    dLon =(long2 - long1)
    x = math.cos(math.radians(lat2)) * math.sin(math.radians(dLon)) 
    y = math.cos(math.radians(lat1)) * math.sin(math.radians(lat2)) - math.sin(math.radians(lat1))* math.cos(math.radians(lat2)) * math.cos(math.radians(dLon)) 
    brng = atan2(x,y)
    brng = degrees(brng)
    return brng

dirs = ["N","nNE","NE","eNE","E","eSE","SE","sSE","S","sSW","SW","wSW","W","wNW","NW","nNW","N"]
def getdirs(deg):
    modeg= int(((deg+360.0+360.0-360/(16*2))%360)/(360/16))+1
    return dirs[modeg]
