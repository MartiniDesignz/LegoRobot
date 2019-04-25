#This file is used for creating distances that corrispond to an existing cordinate


class coord():
    x=0
    y=0



a=coord()
a.x=6
a.y=-6

c=coord()
c.x=6
c.y=114

d=coord()
d.x=102
d.y=114

def dist(pos, t):
    return((t.x-pos.x)**2+(t.y-pos.y)**2)**.5

pos=coord()
pos.x=float(input("Enter x:"))
pos.y=float(input("Enter y:"))

print("Distance a: ", dist(pos, a))
print("Distance c: ", dist(pos, c))
print("Distance d: ", dist(pos, d))
