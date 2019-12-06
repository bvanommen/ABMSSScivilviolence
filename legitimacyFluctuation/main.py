from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic
import numpy as np
import pyqtgraph as pg
import os
from PyQt5.QtGui import QImage, QPixmap
import toolbox
import sys


class main_window(QMainWindow):
    def __init__(self):
        super().__init__()

        # open ui file with same name as this file
        filename = os.path.basename(__file__)
        uifilename = filename[:-2] + "ui"
        uic.loadUi(uifilename, self)

        # Coded Parameters
        self.xWidth = 40
        self.yWidth = 40
        self.agentDens = 0.7
        self.copDens = 0.04
        self.agentVis = 7
        self.copVis = 7
        self.T = 10
        self.periodSlider.setTickPosition(int(self.T))
        self.periodSlider.setSliderPosition(int(self.T))
        self.maxJail = 30
        self.actives = []
        # graph
        self.plotItem = self.graph.getPlotItem()
        self.plotItem.setLabels(bottom='iteration', title="graph")
        self.curveJailed = self.plotItem.plot(pen='g')
        self.curveActive = self.plotItem.plot(pen='r')

        # this timer is not used anymore
        #self.timer = pg.QtCore.QTimer()
        #self.timer.setInterval = 100
        #self.timer.timeout.connect(self.updateView)

        self.workTimer = pg.QtCore.QTimer()
        self.workTimer.setInterval = 100
        self.workTimer.timeout.connect(self.simStep)
        self.pix = QPixmap()

        self.connectUI()
        self.show()
        self.prepareRun()

    def connectUI(self):
        # connect any new buttons or UI elements to a function ehre
        self.startRun.clicked.connect(self.startRunFunc)
        self.stopRun.clicked.connect(self.stopRunFunc)
        self.exportData.clicked.connect(self.exportDataFunc)
        self.periodSlider.valueChanged.connect(self.updatePeriod)
    def startRunFunc(self):

        #self.prepareRun()
        self.its = 0
        self.fields = []
        self.agent_history = []
        self.jailed_agents = []
        #self.timer.start()
        self.workTimer.start()

    def prepareRun(self):
        # set-up
        flatPositions = []
        self.legitimacies = []
        for x in np.arange(self.xWidth):
            for y in np.arange(self.yWidth):
                flatPositions.append("e")
        self.field = np.array(flatPositions).reshape([self.xWidth, self.yWidth])
        # field is an array containing, for each lattice point, whether that point has a:
        # a = active agent
        # i = inactive agent
        # c = cop
        # e = empty
        self.agents = [] # list of all agents
        self.cops = [] # list of all cops
        self.agentNumber = int(self.agentDens * self.xWidth * self.yWidth)
        self.copNumber = int(self.copDens * self.xWidth * self.yWidth)
        self.L = np.array([0.79])

        Rs = np.random.uniform(size=self.agentNumber)
        Hs = np.random.uniform(size=self.agentNumber)
        locationIDs = np.random.choice(np.arange(self.xWidth * self.yWidth),
            size=self.agentNumber + self.copNumber, replace=False)
        locations = [np.floor(locationIDs / self.xWidth), locationIDs % self.xWidth]
        for i in np.arange(self.agentNumber):
            self.agents.append(
                toolbox.agent([locations[0][i], locations[1][i]], Hs[i], Rs[i], self.L,
                    self.agentVis, self.field, self.maxJail))
        for i in np.arange(self.copNumber):
            self.cops.append(toolbox.cop(
                [locations[0][self.agentNumber + i], locations[1][self.agentNumber + i]],
                self.copVis, self.field))

    def simStep(self):

        # Pick agent order at random
        choice = (np.arange(self.agentNumber+self.copNumber))
        np.random.shuffle(choice)
        # currently we choose a random order each simulation step, and
        # have agents act in that order
        if (self.its % self.T == 0):
            self.L[0] = min(1,max(0,0.79+np.random.uniform(-0.3,0.3)))
        for num in choice:
            if num < self.agentNumber:
                a = self.agents[num]
                a.move()
                a.stateTick()
                a.finalStateTick()
            else:
                a = self.cops[num - self.agentNumber]
                a.move()
                a.jail()
        self.its += 1

        self.fields.append(np.copy(self.field)) # save the state of the field each iteration
        # for later analysis
        self.jailed_agents.append(toolbox.count_agents_jailed(self.agents))
        # save how many agents were jailed
        self.legitimacies.append(self.L * 100)
        self.updateImages()
        self.updateView()
        # updates the UI

    def updateView(self):
        """this function puts the image currently in memory into the display,
         and updates the graphs"""
        self.currentFieldLabel.setPixmap(self.pix)
        self.stepNum.setText("Field at Run:" + str(self.its))
        x = np.arange(self.its)
        try:
            self.actives.append(sum(self.fields[-1].flatten() == 'a'))
            self.curveActive.setData(x, self.actives)
        except IndexError:
            pass
        self.curveJailed.setData(x, self.jailed_agents)

    def updatePeriod(self):
        """This function handles the period slider"""
        newT = self.periodSlider.value()
        self.T = newT

    def countActives(self, fields):
        """"""
        #total = sum(fields[0].flatten() == 'a') + sum(fields[0].flatten() == 'i')
        ratios = [] # we used to calculate the ratios, however now we just count the total number
        # of agents
        for curField in fields:
            actives = sum(curField.flatten() == 'a')
            ratios.append(actives)
        return ratios

    def updateImages(self):
        """Creates a new image of the current field"""
        imArr = toolbox.make_image(self.field)
        im_np = np.transpose(imArr, (1, 0, 2)).copy() # gets the image array into the (x,y,3) shape
        self.image = QImage(im_np, imArr.shape[1], imArr.shape[0], QImage.Format_RGB888)
        self.image = self.image.scaled(self.xWidth * 10, self.yWidth * 10)
        self.pix = QPixmap(self.image)

    def stopRunFunc(self):
        """Does not work properly yet. The x and y data of the graphs should also be reset"""
        self.workTimer.stop()

    def exportDataFunc(self):
        """Have not written this function yet. This should save the fields to a file
        It might also help to save the agents as well, to more closely study the agents
        in retrospect"""
        text = self.fileName.text()
        np.savetxt(text,np.transpose([self.actives,self.jailed_agents,self.legitimacies]),fmt="%d")



# This file can be run on its own thanks to the following code

if __name__ == '__main__':

    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    window = main_window()

    app.exec_()
