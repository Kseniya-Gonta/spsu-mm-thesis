# -*- coding: utf-8 -*-
"""
Created on Thu Apr 12 01:49:51 2018
@author: user
"""

import numpy as np
import cvxlib as c
import matplotlib.pyplot as plt
from matplotlib import patches

print 'start'
# set figure
figure, axes = plt.subplots()
xmin, xmax = -1, 2
ymin, ymax = -1.5, 2
axes.set_xlim(xmin, xmax)
axes.set_xlabel('X')
axes.set_ylim(ymin, ymax)
axes.set_ylabel('Y')

# ellipse1
#Q = np.array([[1.2126, -0.6390], 
#              [-0.6390, 0.7474]])
angleDeg = 35
p1 = np.array([[1.66, 0],
               [0, 0.3]])
x1 = np.array([0.5, -0.5])
R = np.array([[np.cos(np.radians(angleDeg)), -np.sin(np.radians(angleDeg))],
              [np.sin(np.radians(angleDeg)), np.cos(np.radians(angleDeg))]])
Q = np.dot(np.dot(R, p1), np.transpose(R))

print 'Q1', Q
pattern = patches.Ellipse((x1[0], x1[1]), 2*p1[0][0], 2*p1[1][1], angleDeg, 
                           edgecolor = 'crimson', fill=False)
axes.add_artist(pattern)
a1 = c.Ellipse()
a1.initByAm(Q, x1)
#______________________________________________________________________________
#ellipse2
#Q = np.array([[.3283, 0.1607],
#              [.1607, 1.2117]])
angleDeg = 100
p2 = np.array([[1.24, 0],
               [0, 0.3]])
x2 = np.array([0.5, 0.5])
R = np.array([[np.cos(np.radians(angleDeg)), -np.sin(np.radians(angleDeg))],
              [np.sin(np.radians(angleDeg)), np.cos(np.radians(angleDeg))]])
Q = np.dot(np.dot(R, p2), np.transpose(R))
#-------------------------------------------------
angle_test = -0.5*np.arctan2(2*Q[0][1],Q[1][1]-Q[0][0])
print 'angle_test', np.degrees(angle_test)
#-------------------------------------------------
print 'Q2', Q
pattern = patches.Ellipse((x2[0], x2[1]), 2*p2[0][0], 2*p2[1][1], angleDeg, edgecolor = 'mediumorchid', fill=False)
axes.add_artist(pattern)
a2 = c.Ellipse()
a2.initByAm(Q, x2)

#______________________________________________________________________________
#ellipse3
#Q = np.array([[.3283, 0.1607],
#              [.1607, 1.2117]])
angleDeg = -90
p3 = np.array([[1.12, 0],
               [0, 0.5]])
x3 = np.array([1, -0.5])
R = np.array([[np.cos(np.radians(angleDeg)), -np.sin(np.radians(angleDeg))],
              [np.sin(np.radians(angleDeg)), np.cos(np.radians(angleDeg))]])
Q = np.dot(np.dot(R, p3), np.transpose(R))
#-------------------------------------------------
angle_test = -0.5*np.arctan2(2*Q[0][1],Q[1][1]-Q[0][0])
print 'angle_test', np.degrees(angle_test)
#-------------------------------------------------
print 'Q3', Q
pattern = patches.Ellipse((x3[0], x3[1]), 2*p3[0][0], 2*p3[1][1], angleDeg, edgecolor = 'darkgreen', fill=False)
axes.add_artist(pattern)
a3 = c.Ellipse()
a3.initByAm(Q, x3)

#find intersection
ellipses = [a1, a2, a3]
D = c.findIntersection(ellipses)
print 'D', D.P, D.x_c

#reconstruction final ellipse
angle = -0.5*np.arctan2(2*D.P[0][1],D.P[1][1]-D.P[0][0])
R = np.array([[np.cos(angle), np.sin(angle)],
             [-np.sin(angle), np.cos(angle)]])
Q = np.dot(np.dot(R, D.P), np.transpose(R))
#print angle
#print Q[0][0], Q[1][1] 
pattern = patches.Ellipse((D.x_c[0], D.x_c[1]), 2*Q[0][0], 2*Q[1][1], np.degrees(angle), edgecolor = 'darkorange', fill=False)
axes.add_artist(pattern)

#draw
figure.canvas.draw()
##additional log
#print D.P, D.x_c
#c.Plot_Ellipse([a2, a1])
#a3 = c.Ellipse()
#a3.initByCQF(a2.A, a2.b, np.dot(np.dot(a2.b.T, np.linalg.matrix_power(a2.A, -1)), a2.b) - 1)
#print 'A', a3.A, 'b', a3.b, 'c', a3.c, a3.P, a3.x_c
print 'end'