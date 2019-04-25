# LegoRobot Advanced Movement Control
# 
# Created by: Robby Martini
#             MartiniDesignz.com
#             martinidesignz@gmail.com
#             github.com/MartiniDesignz
#
# ---------------------------------------------------------------------
# For use of ev3dev2 Library:
#   Copyright (c) 2015 Ralph Hempel <rhempel@hempeldesigngroup.com>
#   Copyright (c) 2015 Anton Vanhoucke <antonvh@gmail.com>
#   Copyright (c) 2015 Denis Demidov <dennis.demidov@gmail.com>
#   Copyright (c) 2015 Eric Pascual <eric@pobot.org>
# ---------------------------------------------------------------------

#Initializing...
from ev3dev2.motor import LargeMotor, MoveTank, OUTPUT_B, OUTPUT_A, OUTPUT_C, MediumMotor
from ev3dev2.motor import SpeedDPS, SpeedRPM, SpeedRPS, SpeedDPM
from ev3dev2.sensor.lego import GyroSensor, ColorSensor, UltrasonicSensor
from ev3dev2.led import Leds
from ev3dev2.sound import Sound
from ev3dev2.display import Display
from threading import Thread
from time import sleep
import math as m

import copy


snd=Sound()
led=Leds()
tP=MoveTank(OUTPUT_A, OUTPUT_B)
g=GyroSensor()
mA=LargeMotor(OUTPUT_A  )
lcd = Display()
cs=ColorSensor()
u=UltrasonicSensor()
med=MediumMotor(OUTPUT_C)



#For colors in Terminal
RED   = "\033[1;31m"  
BLUE  = "\033[1;34m"
CYAN  = "\033[1;36m"
GREEN = "\033[0;32m"
RESET = "\033[0;0m"
BOLD    = "\033[;1m"
REVERSE = "\033[;7m"



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



class obj():#distances are in inches
    def __init__(self, width=0, length=0, height=0,  ang=0, x=0, y=0, cOffx=0, cOffy=0, action=""):
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




# classes----------------------------------------
class coord():
    # Makes it easier to store coordinate values
    x=0
    y=0
    same=[]#list of coords with same x and y

class action():
    # Makes it easier to store comands
    turn=0
    d=0

class lcdStuff():
    #calculated info needed for displaying data to the lcd screen
    #constants of screen
    h=128
    w=178
    #------------
    coords=[]
    border=0
    maxX=0#max x for list of data
    maxY=0#max y for list of data
    minX=0#min x for list of data
    minY=0#min y for list of data
    zeroX=89
    zeroY=64
    sx=1#scale x
    sy=1#scale y


#Create the map----------------------------------------------------------------------------
shvs=[obj(), obj() , obj(), obj(), obj(), obj(), obj(), obj()]


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


robot=obj(6, 10, 5, 90, 0, 0, 0, 0)
coords=[]
idCoords=[]
idRobot=coord()
#the robot needs to have one side(either right or left) constantly 
initCoord=coord()
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

idCoords+=initCoord
idCoords+=initCoord

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


st=0
getStartCoord(st)  
order=getStartCoord(start = st)

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
for w in idCoords:
    if i%4==0:
        print("________________________________\n")
    print("(", w.x, ", ", w.y,")")
    i+=1
    p=w
    


#Done making the map-------------------------------------------------------------------------------------------------


#LEDS----------------------------------------------
    # Description:
    #   Basic functions to controls the leds

def loff():#Turn all LEDs off
    led.all_off() 

def Llr():#left led red
    led.set_color('LEFT', (1, 0)) #Bright Red

def Llg():#left led green
    led.set_color('LEFT', (0, 1)) #Bright Green

def Rlr():#Right led red
    led.set_color('RIGHT', (1, 0)) #Bright Red

def Rlg():#Right led green
    led.set_color('RIGHT', (0, 1)) #Bright Green

    # Effects
def flash(t, s):#Flash LEDs for t (time in sec) at s(flashes per second)
    t/=s
    i=0
    while i<t:
        i+=1
        if i%2==0:
            Llr()
            Rlg()
        else:
            Llg()
            Rlr()
        sleep(s)

def fade(t):#Fade from red to green to red
    i=0
    while i<t:
        i+=1
        p=0
        while p<t*10:
            p+=1
            if i%2==0:
                led.set_color('LEFT', (p/100, 1-p/100)) #Bright Red
                led.set_color('RIGHT', (p/100, 1-p/100)) #Bright Red
            else:
                led.set_color('LEFT', (1-p/100, p/100)) #Bright Red
                led.set_color('RIGHT', (1-p/100, p/100)) #Bright Red
            sleep(.01)


#Displaying to ev3 screen ---------------------------------------------
    # Description
    #   width = 178px
    #   height = 128px
    #   fucntions for displaying info to the ev3 lcd screen

style = 'helvB'
lcdI=lcdStuff()

def dispPos(c, size=24):#display the coords given to the function
    lcd.clear()
    temp="("+str(c.x)+", "+str(c.y)+")"
    y=int((128-size)/2)#calculate the verticle center
    x=50               #guess the horizontal center
    lcd.text_pixels(temp, False, x, y, font=style+str(size))
    lcd.update()

def graphInit(coords, border=20):# Initializing info based on list of coords
    border=abs(border)#ensures border input is positive
    lcdI.border=border
    lcdI.coords=coords
    lcdI.minX=coords[0].x
    lcdI.minY=coords[0].y
    i=0
    for c in coords:#set the min and max for data set
        if c.y>lcdI.maxY:
            lcdI.maxY=c.y
        elif c.y<lcdI.minY:
            lcdI.minY=c.y
        if c.x>lcdI.maxX:
            lcdI.maxX=c.x
        elif c.x<lcdI.minX:
            lcdI.minX=c.x
        k=0
        for u in coords:
            if (c.y==u.y)and(c.x==u.x):
                coords[i].same.append(k)
            k+=1
        i+=1
    rx=abs(lcdI.maxX-lcdI.minX)#ranges
    ry=abs(lcdI.maxY-lcdI.minY) 
    lcdI.sx=(lcdI.w-2*border)/rx#scales
    lcdI.sy=(lcdI.h-2*border)/ry
    lcdI.zeroX=(0-lcdI.minX)*lcdI.sx+border
    lcdI.zeroY=(0-lcdI.minY)*lcdI.sy+border

def drawAxis(w=4):#Draw axis lines based on lcdI
    lcd.line(False, x1=0, y1=128-lcdI.zeroY, x2=lcdI.w, y2=128-lcdI.zeroY, line_color='grey', width=w)#x-axis
    lcd.line(False, x1=lcdI.zeroX, y1=0, x2=lcdI.zeroX, y2=lcdI.h, line_color='grey', width=w)#y-axis

def graphicAction():
    lcd.clear()
    drawAxis()
    for c in lcdI.coords:
        lcd.circle(False, x=c.x*lcdI.sx+lcdI.zeroX, y=128-(c.y*lcdI.sy+lcdI.zeroY), radius=5, fill_color='white', outline_color='black')
    lcd.circle(False, x=pos.x*lcdI.sx+lcdI.zeroX, y=128-(pos.y*lcdI.sy+lcdI.zeroY), radius=5, fill_color='black', outline_color='black')#pos
    lcd.update()


def dotAnim(t=5, speed=.25):# Display . .. ... animation on the screen
        i=0
        while i<(t/speed):
            lcd.clear()
            size=24#max font size
            temp="."*(i%3)
            y=int((128-size)/2)#calculate the verticle center
            x=70               #guess the horizontal center
            lcd.text_pixels(temp, False, x, y, font=style+str(size))
            lcd.update()
            sleep(speed)
            i+=1

#Sensors----------------------------------------------------------------
    # Description:
    #   Functions for testing and checking sensors
    #
def rAng(t=10):#read the gyro for t(seconds)
    t/=.1
    i=0
    while i<t:
        i+=1
        print(g.angle)
        sleep(.1)


def rCol(t=10):#read the gyro for t(seconds)
    t/=.1
    i=0
    while i<t:
        i+=1
        print(cs.color)
        sleep(.1)



def rUlt(t=10):#read the gyro for t(seconds)
    t/=.1
    i=0
    while i<t:
        i+=1
        print(u.distance_inches)
        sleep(.1)


def calW():
    cs.calibrate_white()
#motors------------------------------------------

    # Description:
    #   Basic functions for controlling motors

    # Functions for repedative Calculations
def toDegin(d):#distance cm to degrees
    return d*360/7 #wheel circumference is 7in or 17.78cm

def toDeg(d):#distance cm to degrees
    return d*360/17.78 #wheel circumference is 7in or 17.78cm

def toCm(x):#inches to cm
    return x*2.54

    # Controling
def bon():#turns break on
    tP.on_for_degrees(0, 0, 0, brake=True, block=True)

def boff():#turns break off
    tP.on_for_degrees(0, 0, 0, brake=False, block=False)

def move(x, s=30, cm=False):     #enter distance in cm | If cm=False, distance should be entered in inches
    d=0
    if cm:
        d=x
    else:
        d=toCm(x)
    tP.on_for_degrees(s, s, toDeg(d), brake=True, block=True)

def eStop():#stop all motors
    tP.off(brake=True)

def onSpin(s=50):#spin until eStop is used
    tP.on(-s, s)

def onMove(s=100):#move forward until eStop is used
    tP.on(s, s)


# Movement functions------------------------------------------------


def turn(deg=180, oa=0, s=20, ac=10, i=0):#turn the robot an exact amount of degrees
    deg*=-1# Turning is setup in the opposite direction
    if oa==0:
        oa=g.angle
    if deg>0:# determin direction of spin
        dire=1
    else:
        dire=-1
    ta=g.angle+deg
    print("Original angle: ", oa, " Target: ", ta)
    onSpin(s*dire)
    ang=g.angle
    if ang<ta:
        while ang<ta-ac:
            ang=g.angle
    else:
        while ang>ta+ac:
            ang=g.angle  
    eStop()
    sleep(1)
    ang=g.angle
    if ang>ta+3 or ang<ta-3:
        if i<3:
            turn((ta-g.angle)*-1, s=40, ac=5, i=i+1)
    print("Current angle: ", g.angle, " Target: ", ta)


#complicated movements----------------------------------------------
def track(oa, d=40, s=50):
    dt=0
    tP.on_for_degrees(s, s, toDegin(d), brake=True, block=False)
    size=0
    angAr=[]
    while mA.state[0]=='running':
        angAr.append((g.angle*-1))
        size+=1
    i=0
    while i<size:
        dc=d/size
        ang=(angAr[i]-oa+90)%360
        pos.y+=m.sin(ang*m.pi/180)*dc
        pos.x+=m.cos(ang*m.pi/180)*dc
        dt+=dc
        i+=1
    print("Expected: ", d, "| Actual: ", dt)
    print("(",pos.x, ", ", pos.y,")")



# Based on location movement----------------------------
def pointOld(oa, c):#Take the robot to its exact orgin
    d=m.sqrt((pos.y-c.y)**2+(pos.x-c.x)**2)
    desAng=0
    if ((pos.y==c.y) and (pos.x==c.x)):
            desAng=oa-(g.angle*-1)
            d=0
    elif pos.y==c.y:
        if pos.x<c.x:
            desAng=0
        else:
            desAng=180
    elif pos.x==c.x:
        if pos.y<c.y:
            desAng=90
        else:
            desAng=270
    else:
        tAng=m.atan(abs((pos.y-c.y)/(pos.x-c.x)))*180/m.pi
        if pos.x>c.x:
            if pos.y<c.y:
                desAng=180-tAng
            else: 
                desAng=180+tAng
        elif pos.y>c.y:
            desAng=360-tAng
        else: 
            desAng=tAng
    calc=((g.angle*-1)-oa+90)%360
    print("Desired Angle: ", desAng)
    print("(",pos.x, ", ", pos.y,")")
    print(" Turn: ", desAng-calc, "Move: ", d)
    if (desAng-calc) != 0:
        turn((desAng-calc))
    if d != 0:
        #if d>20:
        track(oa, d)


def point(oa, c):#Take the robot to its exact orgin
    d=m.sqrt((pos.y-c.y)**2+(pos.x-c.x)**2)
    desAng=0
    if ((pos.y==c.y) and (pos.x==c.x)):
            desAng=oa-(g.angle*-1)
            d=0
    elif pos.y==c.y:
        if pos.x<c.x:
            desAng=0
        else:
            desAng=180
    elif pos.x==c.x:
        if pos.y<c.y:
            desAng=90
        else:
            desAng=270
    else:
        tAng=m.atan(abs((pos.y-c.y)/(pos.x-c.x)))*180/m.pi
        if pos.x>c.x:
            if pos.y<c.y:
                desAng=180-tAng
            else: 
                desAng=180+tAng
        elif pos.y>c.y:
            desAng=360-tAng
        else: 
            desAng=tAng
    calc=((g.angle*-1)-oa+90)%360
    print("Desired Angle: ", desAng)
    print("(",pos.x, ", ", pos.y,")")
    print(" Turn: ", desAng-calc, "Move: ", d)
    if (desAng-calc) != 0:
        turn((desAng-calc))
    if d != 0:
        if d>=36:
            scanShelf(oa, d)
        else:
            track(oa, d)


#pre-action functions and calculations-----------------------------------------------

def xytocoords(x, y):
    tCors=[coord()]#initial coord should be 0, 0
    i=0
    while i<len(x):#put the coords into a single class array to make it easier to transfer
        temp=coord()
        temp.x=x[i]
        temp.y=y[i]
        tCors.append(temp)
        print("coord: (",x[i], ", ", y[i], ")")  
        i+=1
    return tCors



#------------------------Scanning Functions---------------------------------------------
def adjust(mindeg, maxdeg, ts):
    i=0
    t=150#durration for adjustment
    s=10
    d=.75#HERE------------------------------------------adjust this for offset of edge of box
    tP.on(0, 0)
    i=0
    while i<t: #mA.state[0]=='running':
        if u.distance_inches<5:
            if u.distance_inches>2.2:
                if(med.degrees<maxdeg ):
                    med.on(0, brake=False)
                else:
                    med.on(-s, brake=False)
            elif(u.distance_inches<2.3 and u.distance_inches>=1.9):
                med.on(0, brake=False)
            else:
                if(med.degrees>mindeg):
                    med.on(0, brake=False)
                else:
                    med.on(s, brake=False)
            i+=1
    med.on(0, brake=False)
    tP.on(-10, -10)
    while True:
        if cs.color==0:
            eStop()
            break
    tP.on_for_degrees(10, 10, toDegin(d), brake=True, block=False)




def scan(s=20):
    cAr=[]#Colors
    i=0
    num=0
    while i<4:#read the barcode
        sleep(.5)
        cAr.append(cs.color)
        tP.on_for_degrees(10, 10, toDegin(.5), brake=True, block=True)
        i+=1
    i=0
    while i<4:#convert to binary array
        if cAr[i]==1:
            cAr[i]=1
        else:
            cAr[i]=0
        i+=1
    i=0
    while i<4:#convert binary to decimal
        num+=(2**(3-i))*cAr[i]
        i+=1
    print(cAr)
    boff()
    return num


def ips(dist_a, dist_c, dist_d):
    temp=coord()
    c = abs((((96*96)+(dist_d*dist_d))-(dist_c*dist_c))/(2*96*dist_d))
    c = m.acos(c)
    c = c * (180/m.pi)
    ang = (90 - c)*m.pi/180
    L1 = dist_d* m.sin(ang)
    x = 102 - L1
    y = m.sqrt(abs((dist_a*dist_a)-((x-6)*(x-6))))-6
    temp.x = x
    temp.y = y
    return temp



def rHome(oa):# get box and go home | Also ask for ips
    # Color sensor is 1.5 inches infront of wheels
    print("\nIm going home\n")
    move(1)
    turn(90)
    move(1)
    move(-6)
    turn(90)
    # Go foward to get the box
    # Back up to the center Line
    # ask for the IPS 
    # Generate path
    # Follow path
    print("____________________________")# Get the inputs
    dist_a=int(input("Enter distance a: "))
    dist_c=int(input("Enter distance c: "))
    dist_d=int(input("Enter distance d: "))
    # Calculate the coords
    the=ips(dist_a, dist_c, dist_d)
    print("(",the.x, ", ", the.y,")")
    pos=the # Set the position to be equal to the coords
    #------------------------------ Create the path for the robot to get home ----------------------
    temp=coord()
    temp.x=initCoord.x
    temp.y=the.y
    theList=[]
    theList.append(the)
    theList.append(temp)
    temp.y=initCoord.y
    theList.append(temp)
    for c in theList:# Go home
        while (abs(abs(pos.x)-abs(c.x))>2) or (abs(abs(pos.y)-abs(c.y))>2):
            pointOld(oa, c)
            graphicAction()
    boff()



def scanShelf(oa, search=10, s=30):
    di=6.1                      # Distance inbetween the center of each box
    track(oa, d=3.05+4)         # Goes from edge of shelf to center of First box (+4 to get to edge of shelf)
    # ang=((g.angle*-1)-oa+90)%360# Get the angle for position calculations
    mindeg=med.degrees      # Limits for the medium motor
    maxdeg=med.degrees-245
    print("min: ", mindeg, "max: ", maxdeg)
    i=0
    while i<6:
        if i>0:
            track(oa, di)
        sleep(.2)
        if (cs.color!=0):
            adjust(mindeg, maxdeg, s)
            result=scan()
            tP.on_for_degrees(s, s, toDegin(1.3125), brake=True, block=True)#go to center of the box
            if result==search:
                i=10
                print("Correct scan")
            else:
                print("Incorrect scan")
        i+=1
        med.on_for_degrees(s, (mindeg-med.degrees), brake=False, block=True)
    print(i)
    if i==11:
        rHome(oa)




def scanShelfOrg(search=10):
    # move 2.5 in to get on to center of the box
    i=0
    di=6.1#Distance inbetween the center of each box
    s=30
    mindeg=med.degrees
    maxdeg=med.degrees-245
    print("min: ", mindeg, "max: ", maxdeg)
    while i<6:
        adj=False
        tP.on_for_degrees(s, s, toDegin(di), brake=True, block=False)
        while mA.state[0]=='running':
            if cs.color!=0:
                if adj==False:
                    adjust(mindeg, maxdeg, s)
                    adj=True
        if adj==True:
            result=scan()
            if result==search:
                i=10
                print("Hello")
            else:
                tP.on(20, 20)
                while True:
                    if cs.color==0:
                        eStop()
                        break
                di=6.1-2
        else:
            di=6.1
        i+=1
        med.on_for_degrees(s, (mindeg-med.degrees), brake=False, block=True)
    print(i)
    # if i==11:
        


#Main function--------------------------------------
pos=coord()#make the position global
pos=initCoord#set the pos coord to be equal to the initcoord

# Enter the coords:
# x=[ 0, 0,  -73, -73, -73, 0]
# y=[ 0, 40, 40, 73, 0, 0]


def final():# task 2 with point to point accuracy
    oa=(g.angle*-1)
    # coords=xytocoords(x, y)
    coords=idCoords
    graphInit(coords)   #setup graph
    for c in idCoords:
        while (abs(pos.x-c.x)>1) or (abs(pos.y-c.y)>1):
            print("_________________________\n")
            print("Current Angle: ", ((g.angle*-1)-oa+90)%360) 
            print("Target coord: (",c.x, ", ", c.y, ")")  
            point(oa, c)
            graphicAction()
            # sleep(1)# sleep 1 second to look at graph
        graphicAction()
    sleep(.5)
    if g.angle-oa*-1 !=0:
        turn(g.angle-oa*-1)# turn to original angle
    boff()




