#Initializing
from ev3dev2.motor import LargeMotor, MoveTank, OUTPUT_B, OUTPUT_A
from ev3dev2.motor import SpeedDPS, SpeedRPM, SpeedRPS, SpeedDPM
from ev3dev2.sensor.lego import GyroSensor
from ev3dev2.led import Leds
from ev3dev2.sound import Sound
from time import sleep
import math as m

snd=Sound()
led=Leds()
tP=MoveTank(OUTPUT_A, OUTPUT_B)
g=GyroSensor()
mA=LargeMotor(OUTPUT_A)
#c=ColorSensor()
#medMot = MediumMotor(OUTPUT_C)


# classes----------------------------------------
class coord():
    x=0
    y=0

class action():
    turn=0
    d=0

#LEDS----------------------------------------------

    # Description:
    #   Basic functions to controls the leds
    #
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


#motors------------------------------------------

    # Description:
    #   Basic functions for controlling motors
    #

    # Calculating
def toDeg(d):#distance cm to degrees
    return d*360/17.78 #wheel circumference is 7in or 17.78cm

def toCm(x):#inches to cm
    return x*2.54

    # Controling
def bon():#turns break on
    tP.on_for_degrees(0, 0, 0, brake=True, block=True)

def boff():#turns break off
    tP.on_for_degrees(0, 0, 0, brake=False, block=False)

def move(x, s=50, cm=True):     #enter distance in cm | If enter inches type False
    if cm:
        d=x
    else:
        d=toCm(x)
    tP.on_for_degrees(s, s, toDeg(d), brake=True, block=True)

def eStop():#stop all motors
    tP.off(brake=True)

def onSpin(s=50):#spin until eStop is used
    tP.on(-s, s)

def onMove(s=50):#move forward until eStop is used
    tP.on(s, s)



# Movement functions------------------------------------------------
     
def turn(deg=180, oa=0, s=20, ac=10):#turn the robot an exact amount of degrees
    deg*=-1
    dire=deg/abs(deg)#direction
    if oa==0:
        oa=g.angle #origninal angle
    
    
    ta=oa+deg#target angle
    onSpin(s*dire)
    while True:
        if g.angle<ta+ac and g.angle>ta-ac:
            eStop()
            break

def backUp(d=-20, s=50, ac=5, inc=10):#Backs the robot up
    mDir=d/abs(d)#movement direction
    i=1
    p=0
    oa=g.angle
    print(mDir)
    while i<inc or p>100:#fix ac
        if oa+ac<g.angle:                                             
            tP.on_for_degrees(s, -s, inc, brake=False, block=True)
        elif oa-ac>g.angle:
            tP.on_for_degrees(-s, s, inc, brake=False, block=True)
        else:
            print(d)
            move(d/inc)
            i+=1
        p+=1 


#complicated movements----------------------------------------------
def track(oa, d=40, s=50):
    dt=0
    tP.on_for_degrees(s, s, toDeg(d), brake=True, block=False)
    size=0
    angAr=[]
    while mA.state[0]=='running':
        angAr.append(g.angle)
        size+=1
    i=0
    while i<size:
        dc=d/size
        ang=(angAr[i]-oa+90)%360
        pos.y+=m.sin(ang*m.pi/180)*dc
        pos.x+=m.cos(ang*m.pi/180)*dc*-1
        dt+=dc
        i+=1
    print("Expected: ", d, "| Actual: ", dt)
    print("(",pos.x, ", ", pos.y,")")
    


def trackBack(oa, d=-20, s=50, ac=5, inc=10):# fuction that tracks the robot and backs up accurately
    mDir=d/abs(d)#movement direction
    i=1
    p=0
    print(mDir)
    dt=0
    size=0
    angAr=[]
    while i<inc or p>100:#fix ac
        #print("Current Angle: ", g.angle, "; Target Angle: ",oa)
        if oa+ac<g.angle:                                                #turn the robot 
            tP.on_for_degrees(s, -s, inc, brake=False, block=True)
        elif oa-ac>g.angle:
            tP.on_for_degrees(-s, s, inc, brake=False, block=True)
        else:
            print(d)
            tP.on_for_degrees(s, s, toDeg(d/inc), brake=True, block=False)
            i+=1
            while mA.state[0]=='running':
                #ult.append(u.distance_centimeters)
                angAr.append(g.angle)
                size+=1
        p+=1
    i=0
    while i<size:
        dc=(d/size)
        ang=(angAr[i]-oa+90)%360
        pos.y+=m.sin(ang*m.pi/180)*dc
        pos.x+=m.cos(ang*m.pi/180)*dc
        dt+=dc
        i+=1
    print("Expected: ", d, "| Actual: ", dt)
    print("(",pos.x, ", ", pos.y,")")



# Based on location movement----------------------------

def final(oa):#Take the robot to its exact orgin (0, 0)
    d=m.sqrt((pos.y)**2+(pos.x)**2)
    desAng=0
    if ((pos.y==0) and (pos.x==0)):
            desAng=oa-g.angle
            d=0
    elif pos.y==0:
        if pos.x<0:
            desAng=0
        else:
            desAng=180
    elif pos.x==0:
        if pos.y<0:
            desAng=90
        else:
            desAng=270
    else:
        tAng=m.atan(abs((pos.y)/(pos.x)))*180/m.pi
        print("Tangent: ", tAng)
        if pos.x>0:
            if pos.y<0:
                desAng=180-tAng
            else: 
                desAng=180+tAng
        elif pos.y>0:
            desAng=360-tAng
        else: 
            desAng=tAng
    print("Desired Angle: ", desAng)
    calc=0
    calc=(g.angle-oa+90)%360
    print("(",pos.x, ", ", pos.y,")")
    print(" Turn: ", desAng-calc, "Move: ", d)
    if (desAng-calc) != 0:
        turn((desAng-calc))
    if d != 0:
        track(oa, d)
    


def point(oa, c):#Take the robot to its exact orgin
    d=m.sqrt((pos.y-c.y)**2+(pos.x-c.x)**2)
    desAng=0
    if ((pos.y==c.y) and (pos.x==c.x)):
            desAng=oa-g.angle
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
        print("Tangent: ", tAng)
        if pos.x>c.x:
            if pos.y<c.y:
                desAng=180-tAng
            else: 
                desAng=180+tAng
        elif pos.y>c.y:
            desAng=360-tAng
        else: 
            desAng=tAng
    print("Desired Angle: ", desAng)
    calc=0
    calc=(g.angle-oa+90)%360
    print("(",pos.x, ", ", pos.y,")")
    print(" Turn: ", desAng-calc, "Move: ", d)
    if (desAng-calc) != 0:
        turn((desAng-calc))
    if d != 0:
        track(oa, d)


#pre-action calculations-----------------------------------------------
def coordToAct(coords):#generates the initial commands for the robot
    acts=[action()]#first action does noting
    i=0
    calcAng=90#starts at 90 deg
    while i<len(coords)-1:
        cur=coords[i]
        nxt=coords[i+1]
        temp=action()
        desAng=0
        d=0
        d=m.sqrt((cur.y-nxt.y)**2+(cur.x-nxt.x)**2)
        if ((cur.y==nxt.y) and (cur.x==nxt.x)):
            desAng=calcAng
            d=0
        elif cur.y==nxt.y:
            if cur.x<nxt.x:
                desAng=0
            else:
                desAng=180
        elif cur.x==nxt.x:
            if cur.y<nxt.y:
                desAng=90
            else:
                desAng=270
        else:
            desAng=m.atan(abs((cur.y-nxt.y)/(cur.x-nxt.x)))*180/m.pi
            if cur.x>nxt.x:
                if cur.y<nxt.y:
                    desAng=180-desAng
                else: 
                    desAng+=180
            elif cur.y>nxt.y:
                desAng=360-desAng
        temp.turn=desAng-calcAng
        temp.d=d
        calcAng=desAng
        acts.append(temp)
        i+=1
    return acts


#Task 2--------------------------------------
pos=coord()#make the position global

def task2():
    coords=[coord()]#initial coord should be 0, 0
    #coords for every thing after initial position
    # x=[0,-30,30, 0]
    # y=[40,40,40, 0]
    x=[ 30,  0,-30, 0]
    y=[ 30, 60, 30, 0]
    i=0
    oa=g.angle
    while i<len(x):#put the coords into a single class array to make it easier to transfer
        temp=coord()
        temp.x=x[i]
        temp.y=y[i]
        coords.append(temp)
        i+=1
    acts=(coordToAct(coords))#generate the initial actions
    i=0
    while i<len(acts):#carry out the actions
        print("_________________________\n")
        print("Turn: ", acts[i].turn, "Move: ", acts[i].d)
        if acts[i].turn != 0:
            turn(acts[i].turn)
        if acts[i].d != 0:
            track(oa, acts[i].d)
        i+=1
    p=0
    turn(g.angle-oa)#turn to original angle
    print("\n----------------Final----------------------\n")
    while True:#go to the starting point
        print("_________________________\n")
        if (abs(pos.x)<3) and (abs(pos.y)<3):
            break
        print("Current Angle: ", (g.angle-oa+90)%360)
        final(oa)
        sleep(.1)
        p+=1
    turn(g.angle-oa)#turn to original angle


def task1():
    oa=g.angle
    d=[50,-30,30,-50]
    for n in d:
        if n<0:
            trackBack(oa, n)
        else:
            track(oa, n)
        sleep(.1)
    while True:#go to the starting point
        if (abs(pos.x)<3) and (abs(pos.y)<3):
            break
        print("------------------------------------ ", pos.y)
        final(oa)
        sleep(.1)
    turn(g.angle-oa)#turn to original angle
        

