# LegoRobot map creation functions and testing
# 
# Created by: Robby Martini
#             MartiniDesignz.com
#             martinidesignz@gmail.com
#             github.com/MartiniDesignz
#




import math as m 
import copy
from tkinter import *

master = Tk() 
w = Canvas(master, width=700, height=700) # 5 pixels for every inch 
w.pack() 




#            C = 1                           D = 3
#    _____________________           _____________________
#   |                     |         |                     |
#   |          4          |         |          8          |
#   |_____________________|         |_____________________|
#
#    _____________________           _____________________
#   |                     |         |                     |
#   |          3          |         |          7          |
#   |_____________________|         |_____________________|
#
#    _____________________           _____________________
#   |                     |         |                     |
#   |          2          |         |          6          |
#   |_____________________|         |_____________________|
#
#    _____________________           _____________________
#   |                     |         |                     |
#   |          1          |         |          5          |
#   |_____________________|         |_____________________|
#
#            A = 0                           B = 2


#Create functions for
#   Creating coord path
#       method for search 
#       method for Goto shelf
#       method for return 
#   0=A a to b to c to d
#   1=B b to c to d to a
#   2=C c to d to a to b
#   3=D d to a to b to c

class coord():
    x=0
    y=0


class obj():#distances are in inches
    def __init__(self, width=0, length=0, height=0, ang=0, x=0, y=0, cOffx=0, cOffy=0, action=""):
        self.width=width   # y distance at angle 0
        self.length=length # x distance at angle 0
        self.height=height
        self.action=action
        self.ang=ang       # angle 0 is on the y axis facing to the right
        self.x=x
        self.y=y
        self.cOffx=cOffx   # By default the "center" point at angle 0 is at the bottom left
        self.cOffy=cOffx
    
    # points rotate around the object clockwise, starting at the bottom left

    # As of right now everything asumes that the angle is 0
    def p1(self):
        temp=coord()
        temp.x=self.x-self.cOffx
        temp.y=self.y-self.cOffy
        return temp

    def p2(self):
        temp=coord()
        temp.x=(self.x-self.cOffx)
        temp.y=(self.y-self.cOffy)+self.width
        return temp
    
    def p3(self):
        temp=coord()
        temp.x=(self.x-self.cOffx)+self.length
        temp.y=(self.y-self.cOffy)+self.width
        return temp
    
    def p4(self):
        temp=coord()
        temp.x=(self.x-self.cOffx)+self.length
        temp.y=(self.y-self.cOffy)
        return temp
    
    def points(self):
        return [self.p1(), self.p2(), self.p3(), self.p4()]

    def check(self, c):
        return (self.x<c.x) and (self.x+self.length>c.x) and (self.y<c.y) and (self.y+self.width>c.y)


#End of Classes---------------------------------------------------------------

shvsdisp=[obj(), obj() , obj(), obj(), obj(), obj(), obj(), obj()]# make global

def createMapdisp():#dimensions are in inches
    i=0
    for shelf in shvsdisp:
        shelf.width=12
        shelf.length=36
        horzLaneGap=12
        shelf.action="avoid"
        if i<4:
            shelf.x=12
            shelf.y=12+(horzLaneGap+shelf.width)*i
        else:
            shelf.x=60
            shelf.y=12+(horzLaneGap+shelf.width)*(i-4)
        i+=1
createMapdisp()#run it

shvs=[obj(), obj() , obj(), obj(), obj(), obj(), obj(), obj()]# make global

def createMap():#dimensions are in inches
    i=0
    for shelf in shvs:
        spacer=4 #4 is ideal but five should be good
        shelf.width=12+spacer*2
        shelf.length=36+spacer*2
        horzLaneGap=12-spacer*2
        shelf.action="avoid"
        if i<4:
            shelf.x=12-spacer
            shelf.y=12+(horzLaneGap+shelf.width)*i-spacer
        else:
            shelf.x=60-spacer
            shelf.y=12+(horzLaneGap+shelf.width)*(i-4)-spacer
        i+=1


createMap()#run it


#Global variables
robot=obj(6, 8, 7, 90, 0, 0, 0, 0)
coords=[]
idCoords=[]
idRobot=coord()
initCoord=coord()

#the robot needs to have one side(either right or left) constantly 

#+3+1 3in cuz thats half the width of the robot 1 in to add space


def getStartCoord(start = 0):
    if start==0:#A
        initCoord.x=6
        initCoord.y=-6
        torder=[0,2,1,3]
    elif start==2:#B
        initCoord.x=102 #10ft
        initCoord.y=-6
        torder=[2,1,3,0]
    elif start==1:#C
        initCoord.x=6
        initCoord.y=114 #10ft
        torder=[1,3,0,2]
    elif start==3:#D
        initCoord.x=102 #10ft
        initCoord.y=114 #10ft
        torder=[3,0,2,1]
    return torder

# Commands:
#   go to vertical lane
#   move verticaly
#   move horizontaly

def com(cp, cc, shelf):
    h=2 # not actual number | find actual number
    temp=coord()
    ar=[]
    if cc.x==cp.x:
        temp.x=cc.x
        if cp.y<cc.y:
            temp.y=cc.y+h
        else:
            temp.y=cc.y-h
    elif cp.x<cc.x:
        temp.y=cc.y
        temp.x=cc.x+h
    else:
        temp.y=cc.y
        temp.x=cc.x-h
    ar+=[temp]
    temp2 = coord()
    temp2.x=temp.x
    if(cc.x<=shelf.x): 
        if (cc.y<=shelf.y):
            temp2.y=shelf.p1().y
        else:
            temp2.y=shelf.p2().y
    else:
        if (cc.y<=shelf.y):
            temp2.y=shelf.p4().y
        else:
            temp2.y=shelf.p3().y
    ar+=[temp2]
    return ar


st=2
getStartCoord(st)  
order=getStartCoord(start = st)


if st==2:#B
    idCoords+=[shvs[4].p4(), shvs[4].p1(), shvs[4].p4()]
elif st==1:#C
    idCoords+=[shvs[3].p2(), shvs[3].p3(), shvs[3].p2()]

idRobot=copy.deepcopy(initCoord)
#generate the ideal points 
j=1
for n in order:  
    i=0
    p=0
    print("N: ", n)
    if  idRobot.y>shvs[2*n+1].y:
        k=-1
        i=1
    else:
        i=0
        k=1
    while i<2 and i>=0:
        tempAr=[]
        if(idRobot.x<=shvs[2*n+i].x): 
            if (idRobot.y<=shvs[2*n+i].y):
                tempAr=[shvs[2*n+i].p1(), shvs[2*n+i].p4(), shvs[2*n+i].p3(), shvs[2*n+i].p2()]
            else:
                tempAr=[shvs[2*n+i].p2(), shvs[2*n+i].p1(), shvs[2*n+i].p4(), shvs[2*n+i].p3(), shvs[2*n+i].p2()]
        else:
            if (idRobot.y<=shvs[2*n+i].y):
                tempAr=[shvs[2*n+i].p4(), shvs[2*n+i].p3(), shvs[2*n+i].p2(), shvs[2*n+i].p1(), shvs[2*n+i].p4()]
            else:
                tempAr=[shvs[2*n+i].p3(), shvs[2*n+i].p2(), shvs[2*n+i].p1(), shvs[2*n+i].p4()]
        idRobot.x=tempAr[len(tempAr)-1].x
        idRobot.y=tempAr[len(tempAr)-1].y
        idCoords+=tempAr
        i+=k
        if p<1:
            idCoords+=com(tempAr[len(tempAr)-2], tempAr[len(tempAr)-1], shvs[2*n+i])
        p+=1
    
    if j<3:
        if  idRobot.y>shvs[2*order[j]+1].y:
            i=1
        else:
            i=0
        idCoords+=com(tempAr[len(tempAr)-2], tempAr[len(tempAr)-1], shvs[2*order[j]+i])
    j+=1

# make a function that creates a list of coords for the robot to take inbetween shelves
 
 
print("\n##########################################################\n\n")


i=0
p=initCoord # past coord()
print("(", p.x, ", ", p.y,")")
w.create_oval(p.x*5+50-5, 650-p.y*5-3, p.x*5+10+50-5, 650-p.y*5+10-3,fill="black")

for g in idCoords:
    if i%4==0:
        print("________________________________\n")
    print("(", g.x, ", ", g.y,")")
    w.create_line(p.x*5+50, 650-p.y*5, g.x*5+50, 650-g.y*5 ) 
    i+=1
    p=g


def printMap(shvsdisp):
    for s in shvsdisp:
        w.create_rectangle(s.p1().x*5+50, 650-s.p1().y*5, s.p3().x*5+50, 650-s.p3().y*5, fill="grey")
printMap(shvsdisp)








mainloop() 
