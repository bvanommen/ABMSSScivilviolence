# Benjamin van Ommen, 23 November 2019
# Implementation of Epstein model
# This file contains the definitions of the agents and cops, and some handy functions
import numpy as np




class agent:
    """The agent should be activated in the order: move, statetick, finalstatetick"""
    def __init__(self, loc, H, R, L, vis, field, maxjail, threshold=0.1):
        """loc = [x,y] position on grid
        H in [0,1] is personal hardship
        R in [0,1] is Risk aversion
        L in [0,1] is regime legitimacy (we start with this being global)
        vis is the vision, the radius in which the agent can see (actually still a square)
        state is 0 or 1, 0 being inactive and 1 being active"""
        self.loc = [int(loc[0]), int(loc[1])]
        self.H = H
        self.R = R
        self.L = L
        self.vis = vis
        self.threshold = threshold
        self.maxJail = maxjail
        self.state = 0
        self.newstate = 0
        self.jailed = 0
        self.remainingJailTime = 0
        self.presence = "i"
        self.field = field  # is only a reference to the global field
        # updating self.field will update the field for all agents
        self.field[int(self.loc[0]), self.loc[1]] = self.presence

    def stateTick(self):
        """Processes the new state of this agent """
        self.loc = [int(self.loc[0]), int(self.loc[1])]
        arrestProb = self.calcArrestProb(self.vis)
        netRisk = self.R * arrestProb
        G = self.H * (1 - self.L)  # grievance
        if ((G - netRisk) > self.threshold) and self.jailed == 0:
            self.newstate = 1 # become angry
        elif self.jailed and self.remainingJailTime > 0:
            self.remainingJailTime -= 1
            self.newstate = 0
        elif self.jailed and self.remainingJailTime == 0:
            self.jailed = 0
            self.newstate = 0
        else:
            self.newstate = 0

    def checkArrested(self):
        """If I have become inactive, while I was active, and I didn't choose so myself,
        then I must have been arrested"""
        if self.field[self.loc[0], self.loc[1]] == 'i' and self.presence == 'a':
            self.jailed = 1
            self.presence = 'i'
            self.remainingJailTime = np.random.randint(0, self.maxJail)

    def updateInternalPresence(self):
        if self.state == 0:
            self.presence = "i"
        elif self.state == 1:
            self.presence = "a"
        self.field[self.loc[0], self.loc[1]] = self.presence

    def finalStateTick(self):
        self.state = self.newstate
        self.updateInternalPresence()

    def calcArrestProb(self, vision, k=2.3):
        """Calculates the arrest probability, given the agent has a given vision
        within which it can see cops and other active agents"""
        C_over_A = np.floor(self.calcCARatio())
        return 1 - np.exp(-k * C_over_A)

    def calcCARatio(self):
        """calculates C/A for this agent"""
        cops, actives = determineSurroundings(self.loc, self.vis, self.field)
        if self.presence == 'i': actives += 1 # always count yourself as active in calculation
        if actives == 0:
            print("something has gone terribly wrong while calculating how many actives I can see")
            # this should never happen, either I am active (then I should at least count myself!)
            # Or I am inactive (in which case I should add 1 to the amount of actives)
        return np.floor(cops / actives)

    def move(self):
        self.checkArrested()
        if self.jailed:
            assert self.presence == "i"
            self.field[self.loc[0], self.loc[1]] = self.presence
        else:
            locs = findx(self.loc, self.vis, 'e',
                self.field)  # find available empty spots within view
            if locs == []: # no available new places to move to
                self.field[self.loc[0], self.loc[1]] = self.presence
            else:
                newPos = locs
                assert self.field[newPos[0], newPos[1]] == 'e'
                # checks if the spot we want to move to is really empty
                # if this is not the case we stop the programme, as then the whole programme state
                # is corrupted
                self.field[self.loc[0], self.loc[1]] = "e" # empty my old spot
                self.field[newPos[0], newPos[1]] = self.presence # move to the new one
                self.loc = newPos # update my own location variable


class cop:
    def __init__(self, loc, copVis, field):
        self.loc = loc
        self.vis = copVis
        self.presence = "c"
        self.intelligentMovement  = 0
        self.field = field
        self.field[int(self.loc[0]), self.loc[1]] = self.presence

    def move(self):
        self.loc = [int(self.loc[0]), int(self.loc[1])]
        if not self.intelligentMovement:
            # find random available empty spots within view
            locs = findx(self.loc, self.vis, 'e', self.field)
        else:
            # Move smartly, into the direction of more active agents
            locs = findxIntel(self.loc,self.vis,self.field)
        if locs == []:
            pass
        else:
            newPos = locs
            assert self.field[newPos[0], newPos[1]] == 'e'
            self.field[self.loc[0], self.loc[1]] = "e"
            self.field[newPos[0], newPos[1]] = self.presence
            self.loc = newPos

    def jail(self):
        self.loc = [int(self.loc[0]), int(self.loc[1])]
        locs = findx(self.loc, self.vis, 'a', self.field)
        # print(locs)
        if locs == []:  # did we find someone?
            pass
        else:
            arrested = locs
            # print(arrested)
            assert self.field[arrested[0], arrested[1]] == 'a'
            self.field[arrested[0], arrested[1]] = 'i'
            # print("arrested!")


def determineSurroundings(loc, vis, field):
    """determines the surroundings of location loc, with a vision vis.
    returns the number of cops and number of actives"""
    xloc = loc[0]
    yloc = loc[1]


    x0 = int(xloc - vis)
    x1 = int(xloc + vis + 1)
    y0 = int(yloc - vis)
    y1 = int(yloc + vis + 1)
    fieldCheckx = field.take(np.arange(x0,x1),axis=0,mode='wrap')
    fieldCheck = fieldCheckx.take(np.arange(y0,y1),axis=1,mode='wrap')
    # these two calls make a 2visx2vis grid which is the vision of the agent/cop
    # we use this to count the number of active agents

    cops = np.sum(fieldCheck.flatten() == "c")
    actives = np.sum(fieldCheck.flatten() == "a")
    return cops, actives

def wrapAround(x,xlen):
    """helper function for findx. Wraps x around if x is smaller or larger than xlen"""
    if x < 0:
        x += xlen
    if x >= xlen:
        x -= xlen
    return x


def findx(loc, vis, z, field,quadMode = 0,quad = [0,0]):
    """returns x,y of a random z within vis. Quadmode allows searching just one quadrature"""
    xloc = loc[0]
    yloc = loc[1]
    xlen = len(field[0,:])
    ylen = len(field[:,0])
    # edges are a problem!

    if not quadMode:
        x0 = int(xloc - vis)
        x1 = int(xloc + vis + 1)
        y0 = int(yloc - vis)
        y1 = int(yloc + vis + 1)
    if quadMode:
        if quad == [1,1]:
            x0 = int(xloc)
            x1 = int(xloc + vis + 1)
            y0 = int(yloc)
            y1 = int(yloc + vis + 1)
        if quad == [1,-1]:
            x0 = int(xloc)
            x1 = int(xloc + vis + 1)
            y0 = int(yloc-vis)
            y1 = int(yloc)
        if quad == [-1,-1]:
            x0 = int(xloc - vis)
            x1 = int(xloc)
            y0 = int(yloc-vis)
            y1 = int(yloc)
        if quad == [-1,1]:
            x0 = int(xloc - vis)
            x1 = int(xloc)
            y0 = int(yloc)
            y1 = int(yloc + vis + 1)
    # plan: randomly choose a location in our vision, check if there's a spot that suffices
    # and return that spot. This makes choosing a random spot to move to, or agent to arrest,
    # much faster, as we can spot searching a lot faster.
    # This will always be faster (or in the edge case it takes just as long) than searching our
    # complete vision.

    found = []
    xPositions = np.arange(x0,x1)
    yPositions = np.arange(y0,y1)
    np.random.shuffle(xPositions)
    np.random.shuffle(yPositions)
    for x in xPositions:
        x = wrapAround(x,xlen)
        for y in yPositions:
            y = wrapAround(y,ylen)
            item = field[x, y]
            if item == z:
                # Found one!
                return [x, y]
                # dist = (x0-x)**2 + (y0-y)**2
    # In case we find nothing, return an empty list
    return []

def findxIntel(loc,vis,field):
    """returns an empty lattice site, if available, in the quadrature with the most active agents.
    If no actives, simply takes a random location"""
    xloc = loc[0]
    yloc = loc[1]
    xlen = len(field[0, :])
    ylen = len(field[:, 0])

    x0 = int(xloc - vis)
    x1 = int(xloc + vis + 1)
    y0 = int(yloc - vis)
    y1 = int(yloc + vis + 1)

    fieldCheckx = field.take(np.arange(x0, x1), axis=0, mode='wrap')
    fieldCheck = fieldCheckx.take(np.arange(y0, y1), axis=1, mode='wrap')

    # we will move towards the quadrature that has the most actives in it
    # 1 is top right, 2 bottom right, 3 bottom left, 4 top left
    quad1 = fieldCheck[vis:2*vis + 1,vis:2*vis + 1]
    quad2 = fieldCheck[vis:2*vis + 1,:vis]
    quad3 = fieldCheck[:vis,:vis]
    quad4 = fieldCheck[:vis,vis:2*vis+1]
    quad1Actives = np.sum(quad1.flatten() == 'a')
    quad2Actives = np.sum(quad2.flatten() == 'a')
    quad3Actives = np.sum(quad3.flatten() == 'a')
    quad4Actives = np.sum(quad4.flatten() == 'a')
    largest = np.argmax([quad1Actives,quad2Actives,quad3Actives,quad4Actives])
    if largest == 0 and quad1Actives == 0:
        return findx(loc,vis,'e',field)
    elif largest == 0:
        quad = [1,1]
    elif largest == 1:
        quad = [1,-1]
    elif largest == 2:
        quad = [-1,-1]
    elif largest == 3:
        quad = [-1,1]
    return findx(loc,vis,'e',field,quadMode = 1,quad = quad)



def Edges(vis):
    a = np.arange(2*vis +1)
    b = np.array((2*vis-1) * [2*vis])
    c = a[::-1] # a reversed
    d = np.array((2*vis-1) * [0])
    return np.concatenate((a,b,c,d))

def searchEdges(vis,loc,field):
    xlen = len(field[0, :])
    ylen = len(field[:, 0])
    xPoss = Edges(vis) + loc[0] - vis
    yPoss = np.roll(Edges(vis), 2 * vis) + loc[1] + 1
    for x in xPoss:
        x = wrapAround(x, xlen)
        for y in yPoss:
            y = wrapAround(y, ylen)
            item = field[x, y]
            if item == 'a':
                biasDir = [wrapAround(x-loc[0],xlen),wrapAround(y-loc[1],ylen)]
                return biasDir
    return []



colormapR = {'i': 0, 'a': 255, 'c': 0, 'e': 255}
colormapG = {'i': 255, 'a': 0, 'c': 0, 'e': 255}
colormapB = {'i': 0, 'a': 0, 'c': 255, 'e': 255}

def make_image(given_field):

    imgArrR = np.vectorize(colormapR.get)(given_field)
    imgArrG = np.vectorize(colormapG.get)(given_field)
    imgArrB = np.vectorize(colormapB.get)(given_field)
    imgArr = np.array([imgArrR, imgArrG, imgArrB])
    imgArrshift = np.moveaxis(imgArr, 0, -1).astype(np.uint8)
    # img = Image.fromarray(imgArrshift.astype(np.uint8),mode = "RGB")
    # im2 = img.resize((500, 500), Image.NEAREST)
    return imgArrshift


def count_agents_jailed(agents):
    total = 0
    agentnum = 0
    for agent in agents:
        agentnum += 1
        if agent.jailed:
            total += 1
    return total


