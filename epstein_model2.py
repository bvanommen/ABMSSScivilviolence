# -*- coding: utf-8 -*-
"""
Created on Mon Dec  2 20:37:23 2019

@author: Ruslan Mushkaev
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Nov  5 15:40:40 2019

@author: Ruslan Mushkaev
"""

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random
import time
import sys


class Agent:
    
    v_a = 3
    L = 0.7
    k = 2.3
    T = 0.1
    
    def __init__(self, R,H,state,pos,jail_term):
        self.R = R # risk aversion
        self.H = H # hardship
        self.state = int(state) # agent state: active or quiet
        self.pos = pos # agent 2d position on grid
        self.jail_term = int(jail_term)
        
    def G(self):
        return self.H*(1-self.L) # grievance
    
    def P(self,grid): # arrest probability
        ratio = self.c2a(grid)
  
        return 1-np.exp(-(self.k)*(ratio))
    
    def N(self,grid): # net risk
        return self.R*self.P(grid)*(self.jail_term)**alpha
    
    def c2a(self,grid): # cop to agent ratio within an agent's visible range
        n = (grid.shape)[0] # square grid side length
        i = (self.pos)[0]
        j = (self.pos)[1]
        N = i-self.v_a
        S = i+self.v_a
        E = j+self.v_a
        W = j-self.v_a
        
        # prevent overflows:
        
        if(N < 0):
            N = 0
        if(S > n-1):
            S = n-1
        if(E > n-1):
            E = n-1
        if(W < 0):
            W = 0
        
        
        nb_agents_loc = 0
        nb_cops_loc = 0
        
        # count numbers of cops and agents within square visible block:
        
        for i in range(N,S+1):
            for j in range(W,E+1):
                if(grid[i,j] == 1): # 1 means agent
                    nb_agents_loc = nb_agents_loc + 1
                elif(grid[i,j] == 2): # 2 means cop
                    nb_cops_loc = nb_cops_loc + 1
        
        return nb_cops_loc/nb_agents_loc
        
    def move(self,grid):
        
        n = (grid.shape)[0]
        i = (self.pos)[0]
        j = (self.pos)[1]
        N = i-self.v_a
        S = i+self.v_a
        E = j+self.v_a
        W = j-self.v_a
        if(N < 0):
            N = 0
        if(S > n-1):
            S = n-1
        if(E > n-1):
            E = n-1
        if(W < 0):
            W = 0
             
        pos_new = random_position(grid,self.pos,N,E,W,S)
        self.pos = pos_new
        grid[i,j] = 0
        grid[pos_new[0],pos_new[1]] = 1
        
        
        
    def rule(self,grid,agent_list):
        if((self.G() - self.N(grid) > self.T) and self.jail_term == 0):
            self.state = int(1)
        else:
            self.state = int(0)
            if(self.jail_term > 0):
                self.jail_term = int(self.jail_term -1) 
#            if(self.jail_term == 0):
#                print("Agent released \n")
    
class Cop:
    
    v_c = 3
    
    def __init__(self,pos):
        self.pos = pos
    
    def move(self,grid):
        
        n = (grid.shape)[0]
        i = (self.pos)[0]
        j = (self.pos)[1]
        N = i-self.v_c
        S = i+self.v_c
        E = j+self.v_c
        W = j-self.v_c
        if(N < 0):
            N = 0
        if(S > n-1):
            S = n-1
        if(E > n-1):
            E = n-1
        if(W < 0):
            W = 0
             
        pos_new = random_position(grid,self.pos,N,E,W,S)
        self.pos = pos_new
        grid[i,j] = 0
        grid[pos_new[0],pos_new[1]] = 2
        
    def rule(self,grid,agent_list):
        random.seed(time.process_time())
        n = (grid.shape)[0]
        i = (self.pos)[0]
        j = (self.pos)[1]
        N = i-self.v_c
        S = i+self.v_c
        E = j+self.v_c
        W = j-self.v_c
        if(N < 0):
            N = 0
        if(S > n-1):
            S = n-1
        if(E > n-1):
            E = n-1
        if(W < 0):
            W = 0
        red_active_agent_list = []
        red_passive_agent_list = []
            
        for i in range(N,S+1):
            for j in range(W,E+1):
                if(grid[i,j] == 1): # for each grid position occupied by an agent:
                    for agent in agent_list: # find the corresponding active agent in agent list and add it to a stack
                        if(((agent.pos)[0] == i) and ((agent.pos)[1] == j)):
                            if(agent.state):
                                red_active_agent_list.append(agent)
                            else:
                                red_passive_agent_list.append(agent)
        if(len(red_active_agent_list)): # randomly arrest one agent from a stack
            agent_ind = random.randint(0,len(red_active_agent_list)-1)
            (red_active_agent_list[agent_ind]).state = 0
            (red_active_agent_list[agent_ind]).jail_term = int(np.random.uniform(0,j_max))
            red_passive_agent_list = non_jailed(red_passive_agent_list)
            if(len(red_passive_agent_list)):
                random.shuffle(red_passive_agent_list)
                if(random.random() <= p):
                    random_agent = red_passive_agent_list[0]
                    random_agent.state = int(1)
                    random_agent.H = 0.9

def random_position(grid,pos,n,e,w,s):
    random.seed(time.process_time())
    index_list = []
    for i in range(n,s+1):
        for j in range(w,e+1):
            if(grid[i,j] == 0):
                index_list.append(np.array([i,j]))
    if(len(index_list)):
        return index_list[random.randint(0,len(index_list)-1)]
    else:
        print("All neighboring sites occupied! \n")
        return pos
    
def agent_update(agent_list):
    
    for agent in agent_list:
        if(agent.jail_term > 0):
            agent.jail_term = int(agent.jail_term -1) 

def non_jailed(agent_list):
    
    non_jailed_list = []
    for agent in agent_list:
        if(agent.jail_term == 0):
            non_jailed_list.append(agent)
    return non_jailed_list

def find_agent(i,j,agent_list):
    for agent in agent_list:
        if(((agent.pos)[0] == i) and ((agent.pos)[1] == j)):
            return agent

def state_grid(grid,agent_list):
    
    state_grid = np.zeros((N,N),dtype = np.int8)
    for i in range(0,N):
        for j in range(0,N):
            if(grid[i,j] == 1): # then agent
                if(find_agent(i,j,agent_list).state):
                    state_grid[i,j] = 3
                else:
                    state_grid[i,j] = 2
            elif(grid[i,j]== 2): # then cop
                state_grid[i,j] = 1
    return state_grid

def active_count(agent_list):
    
    count = 0
    for agent in agent_list:
        if(agent.state == 1):
            count = count + 1
    return count
        
def evolve(agent_list,cop_list,grid):
    entities = agent_list + cop_list
    random.shuffle(entities)
    for entity in entities:
        entity.move(grid)
        entity.rule(grid,agent_list)


N = 20
N_tot = N*N
pop_density = 0.7
cop_density = 0.04
agent_density = pop_density - cop_density
nb_agents = int(N_tot * agent_density)
nb_cops = int(N_tot * cop_density)
grid = np.array([0]*(N_tot-nb_agents-nb_cops)+[1]*nb_agents+[2]*nb_cops)
np.random.shuffle(grid)
grid = grid.reshape(N,N)
j_max = 15
alpha = 0
nb_iters = 500
y = np.linspace(0, 0, nb_iters)
p = 0.8

agent_list = []
cop_list = []

# generate agent and cop list:

for i in range(0,N):
    for j in range(0,N):
        if(grid[i,j] == 1):
            r = np.random.uniform(0,1)
            h = np.random.uniform(0,1)
            state = 0
            pos = np.array([i,j])
            jail_term = int(0)
            agent_list.append(Agent(r,h,state,pos,jail_term))
        elif(grid[i,j] == 2):
            pos = np.array([i,j])
            cop_list.append(Cop(pos))
            
colors = 'k b g r'.split()
cmap = matplotlib.colors.ListedColormap(colors, name='colors', N=None)

fig = plt.figure(1)
ax1 = fig.add_subplot(121)
matrix = ax1.matshow(state_grid(grid,agent_list), cmap = cmap,norm = plt.Normalize(0,3))


ax2 = fig.add_subplot(122)
x, y = [],[]

#sc = ax2.scatter(x,y, s=5)
plt.xlim(0,nb_iters)
plt.ylim(0,300)
plt.title('Active agents')
plt.xlabel('Cycle Number')
plt.ylabel('Count')

#plt.autoscale(enable=True, axis='y',tight=False)

line, = ax2.plot([], [], lw=2, label = 'No modification', color = 'black')
ax2.legend()

for i in range(0,nb_iters):
    print("Iteration # " + str(i)+"\n")
    evolve(agent_list,cop_list,grid)
    x.append(i)
    y.append(active_count(agent_list))

line.set_data(x, y)
plt.show()

# initialization function: plot the background of each frame
#def init():
#    line.set_data([], [])
#    return line,
#
#def update(i,agent_list,cop_list,grid):
#    
#    evolve(agent_list,cop_list,grid)
#    matrix.set_array(state_grid(grid,agent_list))
#    x.append(i)
#    y.append(active_count(agent_list))
##    sc.set_offsets(np.c_[x,y])
#    line.set_data(x, y)
#    return line,
#
#
#ani = animation.FuncAnimation(fig, update, frames=nb_iters,init_func=init, fargs=(agent_list,cop_list,grid), interval=0)
#plt.show()



