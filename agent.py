# -*- coding: utf-8 -*-
"""
Created on Fri Jan 24 23:44:24 2018
 
@author: Anna Leonova
"""
import math
import numpy as np
import measurement as m
 
class Point(object):
   
    def __init__(self, x, y):
        self._data = np.array([x, y], dtype=np.float32)
       
    @property  
    def x(self):
        return self._data[0]
       
    @x.setter
    def x(self, value):
        self._data[0] = value
   
    @property  
    def y(self):
        return  self._data[1]
       
    @y.setter
    def y(self, value):
        self._data[1] = value
   
    @property
    def point(self):
        return self._data
   
    @point.setter
    def point(self, value):
        self._data = value
   
    def add(self, other):
        self._data += other.point
   
    def getDistance(self, other):
        valueX = self.x - other.x
        valueY = self.y - other.y
        return math.sqrt(math.pow(valueX, 2) + math.pow(valueY, 2))
   
    def getAngle(self, other):
        x = other.x - self.x
        y = other.y - self.y
        return math.atan2(y, x)
    
    def polarToCartesian(self, offset): #warning!
        x = offset.x + self.y * math.cos(self.x)
        y = offset.y + self.y * math.sin(self.x)
        return Point(x, y)

class Agent(object):
   
    def __init__(self, x, y, dx, dy):
        """Constructor"""
        self._point = Point(x, y)
        self._speed = Point(dx, dy)
   
    @property
    def x(self):
        return self._point.x
   
    @property
    def y(self):
        return self._point.y
        
    @property
    def dx(self):
        return self._speed.x
   
    @property
    def dy(self):
        return self._speed.y
   
    @property
    def point(self):
        return self._point
   
    def move(self):
        self._point.add(self._speed)
   
       
class AgentTarget(Agent):
   
    def __init__(self, x, y, dx, dy):
        """Constructor"""
        super(AgentTarget, self).__init__(x, y, dx, dy)
 
class AgentSensor(Agent):
   
    def __init__(self, x, y, dx, dy, errLength, errAngle):
        """Constructor"""
        super(AgentSensor, self).__init__(x, y, dx, dy)
        self._point = Point(x, y)
        self._errLength = float(errLength) * 0.01
        self._errAngle = math.radians(float(errAngle))
    
    @property
    def measurements(self):
        return self._measurements
    
    @measurements.setter
    def measurements(self, value):
        self._measurements = value
   
    def getData(self, targets):
        self._measurements = []
        for target in targets: 
            dist = self._point.getDistance(target.point)
            angle = self._point.getAngle(target.point)
  
            #error = np.random.normal(scale = dist * self._errLength) #high emissions
            error = np.random.rand() * dist * self._errLength #only positive
            #error = np.random.standard_normal() * dist * self._errLength #point  - out ellipse
            dist += error
            print 'dist:', dist, 'error', error, 'scale', dist * self._errLength
           
            #error = np.random.normal(scale = self._errAngle)
            error = np.random.rand() * self._errAngle
            #error = np.random.standard_normal() * self._errAngle #point  - out ellipse
            angle += error
            print 'angle:', angle, 'error', error, 'scale', self._errAngle
            measurement = m.MeasurementFromSensor(angle, dist, dist * self._errLength, dist * math.tan(self._errAngle))                        
            self._measurements.append(measurement)
      
if __name__ == "__main__":
    print 'hello!'
    p1 = Point(1, 1)
    p2 = Point(2, 2)
    p1.add(p2)
    print p1.point
    print 't'
    print p1.getAngle(p2)
    print 'rubicon1'
   
    print math.atan2(30, 40)
    m1 = m.MeasurementFromSensor(math.atan2(30, 40), 50, 1, 1)
    print 'm1 point', m1.point.point
    p3 = m1.polarPoint.polarToCartesian(Point(20, 10))
    print 'x y' , p3.point
   
   
   
    