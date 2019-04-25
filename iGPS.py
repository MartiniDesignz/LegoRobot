# LegoRobot iGPS Movement Control
# 
# Created by:  Sarah George (Group member)
#
#
# Description:
#   Calculates a coordinate based on three distance measurements
#


import math as m #importing math library for trig functions

class coord():# create a class for storing coordinates
    x=0
    y=0

def dPos(dist_a, dist_c, dist_d):
    temp=coord()
    c = abs((((96*96)+(dist_d*dist_d))-(dist_c*dist_c))/(2*96*dist_d))
    c = m.acos(c)
    ang = (m.pi/2 - c)#rads
    L1 = dist_d* m.sin(ang)
    x = 102 - L1
    y = m.sqrt(abs((dist_a*dist_a)-((x-6)*(x-6))))-6
    temp.x = x
    temp.y = y
    return temp
    

out=coord()
out=dPos(57, 81, 96)
print("(", out.x, ", ", out.y, ")")
