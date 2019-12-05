import random as rd
import functions as fct
import math


def model1(N,k,T,n_step,L,J_max,v,v_star,pop_d,cop_d,clever_motion=1):
        
    """
    N = 40 # lattice size
    k = math.log(10)
    T = 0.1 # action threshold
    n_step = 100 # number of steps / simulation duration
    L = 0.75 # Legitimacy, same fore every agents
    J_max = 20 # maximum jail term / maximum duration spent in prison
    v = 2 # agent's vision (N,S,E,W)
    v_star = 2 # cop's vision (N,S,E,W)
    pop_d = 0.7 # population density (agents+cops)
    cop_d = 0.08 # cop density (among population) -> cop density in the lattice = cop_d*pop_d
    """

    #titre = 'T='+str(T)+', L='+str(L)+', Jmax='+str(J_max)+', v='+str(v)+', v*='+str(v_star)+', pop. density='+str(pop_d)+', cop density='+str(cop_d) 
    
    
    # definition of the class Agent (pops do not need a class)
    class Agent(object):
        active = 0 # the agent is initialy quiet
        CAv_ratio = 1
        P = 1-math.exp(-k*CAv_ratio)
        def __init__(self):
            self.H = rd.random() # level of hardship
            self.G = self.H*(1-L) # level of grievance
            self.R = rd.random() # level of risk aversion
            self.N = self.R*self.P # agent's net risk


    # creation of the initial lattice
    lattice = []
    
    for i in range(N):
        row = []
        for j in range(N):
            if (rd.random() < pop_d): # the site will be occupied by someone
                if (rd.random() < cop_d): # the site will be occupied by a cop
                    row.append(1)
                else: # the site will be occupied by an agent
                    row.append(Agent())
            else: # the site will b unoccupied
                row.append(0)
        lattice.append(row)


    # initialisation of agent's features
    #fct.lattice_update(lattice,k,v,T)

  
    # iteration of the model
    #time = list(range(n_step))
    nb_jail = []
    nb_active = []
    
    prison = [] # creation of the prison
    
    for step in range(n_step):
    
        i,j = rd.randint(0,N-1),rd.randint(0,N-1)
        while (lattice[i][j] == 0): # selects randomly an agent or a cop
            i,j = rd.randint(0,N-1),rd.randint(0,N-1)
        
        if (lattice[i][j] == 1): # if it is a cop
            if (clever_motion == 1):
                pos = fct.clever_moove(lattice,i,j,v_star) # new position of the cop (can be the same)
            else:
                pos = fct.moove(lattice,i,j,v_star) # new position of the cop (can be the same)
            fct.act_cop(lattice,pos[0],pos[1],v_star,J_max,prison) # the cop acts
        else: # it is an agent
            pos = fct.moove(lattice,i,j,v) # new position of the agent (can be the same)
            fct.agent_update(lattice,pos[0],pos[1],k,v,T) # the agent acts
            #fct.lattice_update(lattice,k,v,T)
    
        nb_jail.append(len(prison))
        if len(prison) > 0:
            k = 0
            while k < len(prison):
                if prison[k][1] > 0:
                    prison[k][1] = prison[k][1] - 1
                elif prison[k][1] == 0:
                    fct.release(lattice,prison[k][0])
                    prison.pop(k) # the agent has served his sentence and is randomly released
                    k = k - 1
                k = k + 1
    
        #fct.display_lattice(lattice)
        nb_active.append(fct.active_number(lattice))
    
    return nb_active,nb_jail