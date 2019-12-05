import math
import numpy as np
import random as rd
import matplotlib.pyplot as plt



def display_lattice(M):
    m = len(M)
    n = len(M[0])
    P = []
    
    for i in range(m):
        row = []
        for j in range(n):
            if (M[i][j] == 0):
                row.append(0)
            elif (M[i][j] == 1):
                row.append(1)
            else:
                row.append(2)
        P.append(row)             
    
    plt.figure()
    plt.imshow(P)
    plt.colorbar()
    plt.show()
        



def agent_update(M,k,l,k_cste,v,T):
    N = len(M) # M must be a square matrix !
    count_A,count_C = 1.0,0.0 # initialises agent/cop counter
    
    for i in range(-v,v+1):
        for j in range(-v,v+1):
            if (k+i >= 0)and(k+i < N)and(l+j >= 0)and(l+j < N):
                if (M[k+i][j+l] == 1):
                    count_C = count_C + 1
                elif (M[k+i][j+l] != 0)and(M[k+i][j+l].active == 1):
                    count_A = count_A + 1
              
    ratio = np.floor(count_C/count_A) #we floor the ratio, like they (accidentally ?) do in Epstein paper
    M[k][l].CAv_ratio = ratio
    M[k][l].P = 1-math.exp(-k_cste*ratio)
    M[k][l].N = M[k][l].R*M[k][l].P
    if (M[k][l].G - M[k][l].N > T):
         M[k][l].active = 1
    else:
         M[k][l].active = 0




def lattice_update(M,k,v,T):
    N = len(M) # M must be a square matrix !
    for i in range(N):
        for j in range(N):
            if (M[i][j] != 0)and(M[i][j] != 1): # if M[i][j] is an agent
                agent_update(M,i,j,k,v,T)

            
                

def moove(M,k,l,vision):
    N = len(M) # M must be a square matrix !
    indices = [] # search empty sites within the vision
    
    for i in range(-vision,vision+1):
        for j in range(-vision,vision+1):
            if (k+i >= 0)and(k+i < N)and(l+j >= 0)and(l+j < N)and(M[k+i][l+j] == 0):
                indices.append([k+i,l+j])
    
    n = len(indices)
    if n > 0: # the agent or cop mooves randomly to an empty site
        r = rd.randint(0,n-1)
        M[indices[r][0]][indices[r][1]] = M[k][l]
        M[k][l] = 0
        return indices[r] # return the new position
    else:
        ret = [k,l]
        return ret
    
    


def clever_moove(M,k,l,v): #for cops 
    N = len(M) # M must be a square matrix !
    boo = 0
        
    for i in range(-v,v+1):
        for j in range(-v,v+1):
            if (k+i >= 0)and(k+i < N)and(l+j >= 0)and(l+j < N)and(M[k+i][l+j] != 0)and(M[k+i][l+j] != 1)and(M[k+i][l+j].active == 1):
                boo = 1
    
    if (boo == 0):
        return moove(M,k,l,v)
    else:
        indices_East = [] #free sites
        c_East = 0 # counts  the number of active agents
        indices_West = []
        c_West = 0
        for i in range(-v,v+1):
            for j in range(1,3):
                if (k+i >= 0)and(k+i < N)and(l+j >= 0)and(l+j < N)and(M[k+i][l+j] != 0)and(M[k+i][l+j] != 1)and(M[k+i][l+j].active == 1):
                    c_East = c_East + 1
                if (k+i >= 0)and(k+i < N)and(l+j >= 0)and(l+j < N)and(M[k+i][l+j] == 0):
                    indices_East.append([k+i,l+j])
        for i in range(-v,v+1):
            for j in range(-2,0):
                if (k+i >= 0)and(k+i < N)and(l+j >= 0)and(l+j < N)and(M[k+i][l+j] != 0)and(M[k+i][l+j] != 1)and(M[k+i][l+j].active == 1):
                    c_West = c_West + 1
                if (k+i >= 0)and(k+i < N)and(l+j >= 0)and(l+j < N)and(M[k+i][l+j] == 0):
                    indices_West.append([k+i,l+j])
        if (c_East >= c_West):
            if (len(indices_East) > 0):
                r = rd.randint(0,len(indices_East)-1)
                M[indices_East[r][0]][indices_East[r][1]] = M[k][l]
                M[k][l] = 0
                return indices_East[r]
            else:
                return moove(M,k,l,v)
        else:
            if (len(indices_West) > 0):
                r = rd.randint(0,len(indices_West)-1)
                M[indices_West[r][0]][indices_West[r][1]] = M[k][l]
                M[k][l] = 0
                return indices_West[r]
            else:
                return moove(M,k,l,v)




def act_cop(M,k,l,vision,J_max,prison):
    N = len(M) # M must be a square matrix !
    indices = [] # search sites within the vision occupied by active agents
    
    for i in range(-vision,vision+1):
        for j in range(-vision,vision+1):
            if (k+i >= 0)and(k+i < N)and(l+j >= 0)and(l+j < N)and(M[k+i][l+j] != 0)and(M[k+i][l+j] != 1)and(M[k+i][l+j].active == 1):
                indices.append([k+i,l+j])
    
    n = len(indices)
    if n > 0: # else the cops does not do anything
        r = rd.randint(0,n-1) # the cop chooses randomly an active agent
        J = rd.randint(1,J_max) # number of steps during which the arrested active agent will stay in prison
        prison.append([M[indices[r][0]][indices[r][1]],J])
        M[indices[r][0]][indices[r][1]] = 0
    
        


def release(M,A):
    N = len(M) # M must be a square matrix !
    indices = []
    for i in range(N):
        for j in range(N):
            if (M[i][j] == 0):
                indices.append([i,j])
    n = len(indices)
    if n > 0: # it is the case if the initial population density is smaller than 1
        r = rd.randint(0,n-1)
        M[indices[r][0]][indices[r][1]] = A




def active_number(M):
    c = 0
    N = len(M) # M must be a square matrix !
    for i in range(N):
        for j in range(N):
            if (M[i][j] != 0)and(M[i][j] != 1)and(M[i][j].active == 1): # if M[i][j] is an active agent
                c = c + 1
    return c