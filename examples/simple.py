from reacty import reactive
from math import sqrt

import logging

logging.basicConfig(level=logging.INFO)

@reactive.class_
class C:
    pass

sqrt_=reactive.fun_(sqrt)

c1=C()

c1.a=1
print("Value",c1.a)
print("Reference",c1.a_)
print("Expression with reference",c1.a_*2+1)

print("Setting Value")
c1.b=sqrt(c1.a*3)
print(c1.b)

print("Setting Expression")
c1.b=sqrt_(c1.a_+3)
c1.c=c1.b_**2-3
c1.d=3*c1.b_
print(c1.b,c1.c,c1.d)

print("Update value, recomputation")
c1.a=5
print(c1.b,c1.c,c1.d)

print("Update value, recomputation")
c1.a=15
print(c1.b,c1.c,c1.d)

#print("Update value, recomputation")
#c1.lst=[]



