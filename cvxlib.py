import cvxpy as cvx
import numpy as np
from matplotlib import patches
import matplotlib.pyplot as plt
from scipy.linalg import fractional_matrix_power as f_matrix_power

class Ellipse:
    def initByAm(self, P, x_c):
        self.P = np.array(P)
        self.x_c = np.array(x_c)
        self.CQF_Representation()
        
    def initByCQF(self, A, b, c):
        self.A = np.array(A)
        self.b = np.array(b)
        self.c = c
        self.Am_Representation()
           
    #check - ok
    def CQF_Representation(self):
        self.A = np.linalg.matrix_power(self.P, -2)
        self.b = np.dot(-self.A, self.x_c)
        self.c = np.dot(np.dot(self.x_c.T, self.A),self.x_c) - 1
    #check - ok
    def Am_Representation(self):
        temp = np.dot(np.dot(self.b.T, np.linalg.matrix_power(self.A, -1)), self.b) 
        self.P = np.dot(np.sqrt(temp - self.c), f_matrix_power(self.A, -0.5))
        self.x_c = np.dot(-np.linalg.matrix_power(self.A, -1), self.b)
        
def plotEllipse(ellipses):#don't work
    p = len(ellipses)
    i = 0
    while(i < p):
        angle = 0.5*np.arctan2(2*ellipses[i].P[0][1],ellipses[i].P[1][1]-ellipses[i].P[0][0])
        R = np.array([[np.cos(angle), -np.sin(angle)],
                      [np.sin(angle), np.cos(angle)]])
        Q = np.dot(np.dot(R, ellipses[i].P), np.transpose(R))
        print 'angle:', angle*180
        print 'R:', R
        print 'P', ellipses[i].P
        print Q
        a = plt.subplot(111, aspect='equal')
        Temp_ellipse = patches.Ellipse(ellipses[i].x_c, 2*np.sqrt(Q[0][0]), 2*np.sqrt(Q[1][1]), -angle*180)
        print 'a', Q[0][0], 'b', Q[1][1]
        a.add_artist(Temp_ellipse)
        Temp_ellipse.set_clip_box(a.bbox)
        Temp_ellipse.set_alpha(0.1)
        a.add_artist(Temp_ellipse)
        i += 1
    #test = patches.Ellipse([0,0], 1, 0.5, 45)
    #a.add_artist(test)
    plt.xlim(-1, 1)
    plt.ylim(-1.5, 1.5)
    plt.show()

def findIntersection(ellipses):
    #Set the number of paramers
    n = 2;
    #Get the number of ellipses
    p = len(ellipses)
    #Find an intersection:
    #Create a variable that is constrained to the positive semidefinite cone.
    #A = cvx.semidefinite(n)
    A = cvx.Semidef(n)
    b = cvx.Variable(n) # Column vector
    tau = cvx.Variable(p)
    obj = cvx.Minimize(-cvx.log_det(A))
    #Set constraint
    ellipses_sum = np.zeros((2 * n + 1, 2 * n + 1))
    i = 0
    while(i < p):
        Matrix_one = np.column_stack((ellipses[i].A, ellipses[i].b, np.zeros((n, n))))
        Matrix_two = np.hstack((np.reshape(ellipses[i].b, (1, n)), np.reshape(ellipses[i].c, (1, 1)), np.reshape(np.zeros(n), (1, n))))
        Matrix_all = np.vstack((Matrix_one, Matrix_two, np.zeros((n, 2 * n + 1))))
        ellipses_sum = ellipses_sum + tau[i] * Matrix_all
        i += 1
        #tau(i)*[[ellipses(i).A, ellipses(i).b, np.zeros((n, n))],
        #        [ellipses(i).b.T, ellipses(i).c, np.zeros((1, n))],
        #        [np.zeros((n, 2*n+1))]]
    Matrix_one = cvx.hstack(A, b, np.zeros((n, n)))
    Matrix_two = cvx.hstack(b.T, -1, b.T)
    Matrix_three = cvx.hstack(np.zeros((n, n)), b, -A)
    Matrix_Ad = cvx.vstack(Matrix_one, Matrix_two, Matrix_three)
    #Matrix_Ad = [[A, b, np.zeros((n, n))],
    #            [b.T, -1, b.T],
    #            [np.zeros((n, n)), b, -A]]
    constraints = [tau >= 0, Matrix_Ad - ellipses_sum << 0]
    # Form and solve optimization problem
    prob = cvx.Problem(obj, constraints)
    prob.solve()
    if prob.status != cvx.OPTIMAL:
        raise Exception('CVXPY Error')
    #output values
    result = Ellipse()
    temp_c = np.array(np.dot(np.dot(b.value.T, np.linalg.matrix_power(A.value, -1)), b.value) - 1)
    result.initByCQF(np.array(A.value), np.array(b.value).reshape(-1), temp_c[0][0]) #remove the crutches!!!!!
    return result
    