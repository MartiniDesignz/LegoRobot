# LegoRobot Advanced Movement Control
# 
# Created by: Robby Martini
#             MartiniDesignz.com
#             martinidesignz@gmail.com
#             github.com/MartiniDesignz
#
#
# ---------------------------------------------------------------------
# For use of ev3dev2 Library:
#   Copyright (c) 2015 Ralph Hempel <rhempel@hempeldesigngroup.com>
#   Copyright (c) 2015 Anton Vanhoucke <antonvh@gmail.com>
#   Copyright (c) 2015 Denis Demidov <dennis.demidov@gmail.com>
#   Copyright (c) 2015 Eric Pascual <eric@pobot.org>
# ---------------------------------------------------------------------



#Initializing...
from ev3dev2.motor import LargeMotor, MoveTank, OUTPUT_B, OUTPUT_A
from ev3dev2.motor import SpeedDPS, SpeedRPM, SpeedRPS, SpeedDPM
from ev3dev2.sensor.lego import GyroSensor
from ev3dev2.led import Leds
from ev3dev2.sound import Sound
from ev3dev2.display import Display
from threading import Thread
from time import sleep
import math as m

snd=Sound()
led=Leds()
tP=MoveTank(OUTPUT_A, OUTPUT_B)
g=GyroSensor()
mA=LargeMotor(OUTPUT_A)
lcd = Display()



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

def graphInit(coords, border=10):# Initializing info based on list of coords
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


#motors------------------------------------------

    # Description:
    #   Basic functions for controlling motors
    #

    # Functions for repedative Calculations
def toDeg(d):#distance cm to degrees
    return d*360/17.78 #wheel circumference is 7in or 17.78cm

def toCm(x):#inches to cm
    return x*2.54

    # Controling
def bon():#turns break on
    tP.on_for_degrees(0, 0, 0, brake=True, block=True)

def boff():#turns break off
    tP.on_for_degrees(0, 0, 0, brake=False, block=False)

def move(x, s=50, cm=True):     #enter distance in cm | If cm=False, distance should be entered in inches
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
     
def turn(deg=180, oa=0, s=30, ac=10):#turn the robot an exact amount of degrees
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
    
    
    


def trackBack(oa, d=-20, s=50, ac=5, inc=10):# fuction that tracks the robot and backs up accurately
    mDir=d/abs(d)#movement direction
    i=1
    p=0
    print(mDir)
    dt=0
    size=0
    angAr=[]
    while i<inc or p>100:#fix ac
        ang=g.angle*-1
        #print("Current Angle: ", g.angle, "; Target Angle: ",oa)
        if oa+ac<ang:                                                #turn the robot 
            tP.on_for_degrees(-s, s, inc, brake=False, block=True)
        elif oa-ac>ang:
            tP.on_for_degrees(s, -s, inc, brake=False, block=True)
        else:
            print(d)
            tP.on_for_degrees(s, s, toDeg(d/inc), brake=True, block=False)
            i+=1
            while mA.state[0]=='running':
                #ult.append(u.distance_centimeters)
                angAr.append(g.angle*-1)
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
            desAng=oa-(g.angle*-1)
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
        if pos.x>0:
            if pos.y<0:
                desAng=180-tAng
            else: 
                desAng=180+tAng
        elif pos.y>0:
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
        track(oa, d)


#pre-action functions and calculations-----------------------------------------------
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

def xytocoords(x, y):
    tCors=[coord()]#initial coord should be 0, 0
    i=0
    while i<len(x):#put the coords into a single class array to make it easier to transfer
        temp=coord()
        temp.x=x[i]
        temp.y=y[i]
        tCors.append(temp)
        i+=1
    return tCors

# Task 1-------------------------------------

dist=[50,-30,30,-50] 

def task1():
    oa=g.angle*-1
    for n in dist:
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
    turn(g.angle-oa*-1)#turn to original angle

#Task 2--------------------------------------
pos=coord()#make the position global

# Enter the coords:
x=[ 30,  0,-30, 0]
y=[ 30, 60, 30, 0]

def task2faster():#pre-calculates actions and then does only thos actions till the end
    oa=(g.angle*-1)
    coords=xytocoords(x, y)
    acts=(coordToAct(coords))#generate the initial actions
    graphInit(coords)   #setup graph
    i=0
    while i<len(acts):#carry out the actions
        print("_________________________\n")
        print("Turn: ", acts[i].turn, "Move: ", acts[i].d)
        graphicAction()
        sleep(1)#sleep .5 second to look at graph
        if acts[i].turn != 0:
            turn(acts[i].turn)
        if acts[i].d != 0:
            track(oa, acts[i].d)
        i+=1
    p=0
    graphicAction()
    sleep(1)#sleep .5 second to look at graph
    turn(g.angle-oa*-1)#turn to original angle
    print("\n----------------Final----------------------\n")
    while True:#go to the starting point
        print("_________________________\n")
        if (abs(pos.x)<3) and (abs(pos.y)<3):
            break
        print("Current Angle: ", ((g.angle*-1)-oa+90)%360)
        final(oa)  
        graphicAction()
        sleep(1)#sleep 1 second to look at graph
        p+=1
    turn(g.angle-oa*-1)#turn to original angle
    sleep(.5)
    boff()


def task2():# task 2 with point to point accuracy
    oa=(g.angle*-1)
    coords=xytocoords(x, y)
    graphInit(coords)   #setup graph
    for c in coords:
        while (abs(abs(pos.x)-abs(c.x))>2) and (abs(abs(pos.y)-abs(c.y))>2):
            print("_________________________\n")
            print("Current Angle: ", ((g.angle*-1)-oa+90)%360)   
            point(oa, c)
            graphicAction()
            sleep(1)# sleep 1 second to look at graph
        if g.angle-oa*-1 !=0:
            turn(g.angle-oa*-1)# turn to original angle
    sleep(.5)
    boff()
