#Initializing...
from ev3dev2.motor import LargeMotor, MoveTank, OUTPUT_B, OUTPUT_A, OUTPUT_C, MediumMotor
from ev3dev2.motor import SpeedDPS, SpeedRPM, SpeedRPS, SpeedDPM
from ev3dev2.sensor.lego import GyroSensor, ColorSensor, UltrasonicSensor
from time import sleep
import math as m

tP=MoveTank(OUTPUT_A, OUTPUT_B)
g=GyroSensor()
mA=LargeMotor(OUTPUT_A)
cs=ColorSensor()
u=UltrasonicSensor()
med=MediumMotor(OUTPUT_C)


#motors------------------------------------------

    # Description:
    #   Basic functions for controlling motors

    # Functions for repedative Calculations
def toDeg(d):#distance cm to degrees
    return d*360/17.78 #wheel circumference is 7in or 17.78cm

def toDegin(d):#distance cm to degrees
    return d*360/7 #wheel circumference is 7in or 17.78cm

def toCm(x):#inches to cm
    return x*2.54

    # Controling
def bon():#turns break on
    tP.on_for_degrees(0, 0, 0, brake=True, block=True)

def boff():#turns break off
    tP.on_for_degrees(0, 0, 0, brake=False, block=False)

def move(x, s=15, cm=False, b=True):     #enter distance in cm | If cm=False, distance should be entered in inches
    # if cm:
    #     d=x
    # else:
    #     d=toCm(x)
    tP.on_for_degrees(s, s, toDegin(x), brake=True, block=b)

def eStop():#stop all motors
    tP.off(brake=True)

def onSpin(s=50):#spin until eStop is used
    tP.on(-s, s)

def onMove(s=100):#move forward until eStop is used
    tP.on(s, s)



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
#seems like it needs to be .5 in for acurate readings

def calW():
    cs.calibrate_white()

def turn(deg=180, oa=0, s=30, ac=10, i=0):#turn the robot an exact amount of degrees
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


def avg(xAr):
    s=0
    i=0
    for x in xAr:
        s+=x
        i+=1
    return (s/i)



# Make a function that scans an entire shelf

# def scan(d=10, s=30):
#     cAr=[]#Colors
#     tP.on_for_degrees(s, s, toDeg(d), brake=False, block=False)
#     while mA.state[0]=='running':
#         if cs.color!=0:
#             cAr.append((cs.color))













def adjust(mindeg, maxdeg, ts):
    i=0
    t=150
    s=20
    d=.85#HERE------------------------------------------adjust this for offset of edge of box
    tP.on(0, 0)
    i=0
    while i<t: #mA.state[0]=='running':
        if u.distance_inches<5:
            if u.distance_inches>2.2:
                if(med.degrees<maxdeg ):
                    med.on(0, brake=False)
                else:
                    med.on(-s, brake=False)
            elif(u.distance_inches<=2.2 and u.distance_inches>=2.0):
                med.on(0, brake=False)
            else:
                if(med.degrees>mindeg):
                    med.on(0, brake=False)
                else:
                    med.on(s, brake=False)
            i+=1
    tP.on(-10, -10)
    while True:
        if cs.color==0:
            eStop()
            break
    tP.on_for_degrees(10, 10, toDegin(d), brake=True, block=False)





def scan(d=20, s=20):
    cAr=[]#Colors
    tP.on_for_degrees(s, s, toDegin(d), brake=True, block=False)
    adj=False
    mindeg=med.degrees
    maxdeg=med.degrees-245
    print("min: ", mindeg, "max: ", maxdeg)
    while mA.state[0]=='running':
        if cs.color!=0:
            if adj==False:
                adjust(mindeg, maxdeg, s)
                adj=True
        # dAr.append(int(u.distance_inches*10)/10)
    i=0
    while i<4:
        sleep(.5)
        cAr.append(cs.color)
        tP.on_for_degrees(10, 10, toDegin(.5), brake=True, block=True)
        i+=1
    print(cAr)
    med.on_for_degrees(s, (mindeg-med.degrees), brake=False, block=True)
    boff()

