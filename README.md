# LegoRobot
This is my code for the lego robot project at UC.  This project includes a library that for the ev3 brick (More info at bottom).  The adv.py file contains a bunch of useful functions for basic movements all and led control as well as complicated functions for movement based on a coordinate system.

<br>

## In-Depth description of task2()
Based on list of coordinates that it is provided it will calculate a list of actions so that the robot passes through each one of those points.  Once the list of actions is created, the robot will then carry out those actions.  While it is moving it tracks its position by using a gyro and assuming that linear movement is consistent.  Once the list of actions has been carried out,the robot will then go to its origin point (0,0), based on its current position.

<br>
<br>

---

### For the Ev3 library
Copyright (c) 2015 Ralph Hempel <rhempel@hempeldesigngroup.com><br>
Copyright (c) 2015 Anton Vanhoucke <antonvh@gmail.com><br>
Copyright (c) 2015 Denis Demidov <dennis.demidov@gmail.com><br>
Copyright (c) 2015 Eric Pascual <eric@pobot.org><br>
