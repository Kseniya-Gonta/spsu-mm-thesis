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

def distributeSensors(ellipses, alpha):
    #Set the number of paramers
    n = 2;
    #Get the number of targets and sensors
    m = ellipses.shape[0]
    p = ellipses.shape[1]
    #Create resource matrix
    tau = cvx.Variable(m, p)
    #Create a variable that is constrained to the positive semidefinite cone.
    A = []
    b = [] # Column vector
    for i in range(m):
        A.append(cvx.Semidef(n))
        b.append(cvx.Variable(n))
        
    #Set objective
    objSum = 0
    for i in range(m):
        objSum += -cvx.log_det(A[i]) + alpha * cvx.norm(tau[i,:], 1)
    obj = cvx.Minimize(objSum)
    
    #Set constraint
    constraints = [tau >= 0]
    for i in range(m):
        ellipses_sum = np.zeros((2 * n + 1, 2 * n + 1))
        for j in range(p):
            #tau(i)*[[ellipses(i).A, ellipses(i).b, np.zeros((n, n))],
            #        [ellipses(i).b.T, ellipses(i).c, np.zeros((1, n))],
            #        [np.zeros((n, 2*n+1))]]
            Matrix_one = np.column_stack((ellipses[i, j].A, ellipses[i, j].b, np.zeros((n, n))))
            Matrix_two = np.hstack((np.reshape(ellipses[i, j].b, (1, n)), np.reshape(ellipses[i, j].c, (1, 1)), np.reshape(np.zeros(n), (1, n))))
            Matrix_all = np.vstack((Matrix_one, Matrix_two, np.zeros((n, 2 * n + 1))))
            ellipses_sum = ellipses_sum + tau[i, j] * Matrix_all
            
        #Matrix_final = [[A, b, np.zeros((n, n))],
        #                [b.T, -1, b.T],
        #                [np.zeros((n, n)), b, -A]]
        Matrix_one = cvx.hstack(A[i], b[i], np.zeros((n, n)))
        Matrix_two = cvx.hstack(b[i].T, -1, b[i].T)
        Matrix_three = cvx.hstack(np.zeros((n, n)), b[i], -A[i])
        Matrix_final = cvx.vstack(Matrix_one, Matrix_two, Matrix_three)
        constraints.append(Matrix_final - ellipses_sum << 0)
        
    #Form and solve optimization problem
    prob = cvx.Problem(obj, constraints)
    prob.solve(verbose=True, max_iters=1000, refinement = 2)
    if prob.status != cvx.OPTIMAL:
        raise Exception('CVXPY Error')
    
    #Form output
    final_ellipses = []
    for i in range(m):
        e = Ellipse()
        temp_c = np.array(np.dot(np.dot(b[i].value.T, np.linalg.matrix_power(A[i].value, -1)), b[i].value) - 1)
        e.initByCQF(np.array(A[i].value), np.array(b[i].value).reshape(-1), temp_c[0][0])
        final_ellipses.append(e)
    return tau.value, final_ellipses
    
def findIntersection(ellipses):
    #Set the number of paramers
    n = 2;
    #Get the number of ellipses
    p = len(ellipses)
    #Find an intersection:
    #Create a variable that is constrained to the positive semidefinite cone.
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
    prob.solve(verbose=True, max_iters=1000, refinement = 2)
    if prob.status != cvx.OPTIMAL:
        raise Exception('CVXPY Error')
    #output values
    result = Ellipse()
    temp_c = np.array(np.dot(np.dot(b.value.T, np.linalg.matrix_power(A.value, -1)), b.value) - 1)
    result.initByCQF(np.array(A.value), np.array(b.value).reshape(-1), temp_c[0][0]) #remove the crutches!!!!!
    return result
    