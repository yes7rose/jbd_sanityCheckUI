"""
Created by James Dunlop
2016
"""
from PySide.QtGui import *
from PySide.QtCore import *
import os, sys, yaml, logging
from functools import partial
logger = logging.getLogger(__name__)
import lib.sanity as sanity
import lib.CONST as CONST
import maya.cmds as cmds
reload(sanity)

class SanityUI(QMainWindow):
    def __init__(self, parent = None):
        QMainWindow.__init__(self, parent)
        self.setWindowTitle('Sanity Check')
        self.setObjectName('Sanity Check')
        self.mainLayout = QVBoxLayout(self)
        self.state = 'rig'
        self.checkBoxes = []
        self.reports = []
        self._initCheckDock()
        self._initCheckBoxes()
        self._initChecksPassed()
        self.tabWidget = QStackedWidget(self)
        self.setCentralWidget(self.tabWidget)
        self.addToolBar(self._initToolBar())
        self.mainLayout.addStretch(1)

        self.resize(1200, 600)

    def _initToolBar(self):
        self.toolBar = QToolBar(self)
        self.toolBar.setFloatable(False)
        self.toolBar.setMovable(False)
        self.toolBar.setAllowedAreas(Qt.TopToolBarArea)
        self.mdlAction = QAction('mdl', self)
        ic = QIcon("{}/iconmonstr-cube-11-240.png" .format(CONST.ICONPATH))
        self.mdlAction.setIcon(ic)
        self.mdlAction.setToolTip('Set checks for modeling dept')
        self.mdlAction.triggered.connect(partial(self._initCheckBoxes, stateCB = 'mdl'))

        self.rigAction = QAction('rig', self)
        ic = QIcon("{}/iconmonstr-magic-6-240.png" .format(CONST.ICONPATH))
        self.rigAction.setIcon(ic)
        self.rigAction.setToolTip('Set checks for rig dept')
        self.rigAction.triggered.connect(partial(self._initCheckBoxes, stateCB = 'rig'))

        self.animAction = QAction('anim', self)
        ic = QIcon("{}/iconmonstr-direction-10-240.png" .format(CONST.ICONPATH))
        self.animAction.setIcon(ic)
        self.animAction.setToolTip('Set checks for anim dept')
        self.animAction.triggered.connect(partial(self._initCheckBoxes, stateCB = 'anim'))

        self.lightAction = QAction('light', self)
        ic = QIcon("{}/iconmonstr-light-bulb-16-240.png" .format(CONST.ICONPATH))
        self.lightAction.setIcon(ic)
        self.lightAction.setToolTip('Set checks for lighting dept')
        self.lightAction.triggered.connect(partial(self._initCheckBoxes, stateCB = 'light'))

        self.toolBar.addAction(self.mdlAction)
        self.toolBar.addAction(self.rigAction)
        self.toolBar.addAction(self.animAction)
        self.toolBar.addAction(self.lightAction)
        self.toolBar.addSeparator()

        self.performChecks = QPushButton(QIcon("{}/iconmonstr-log-out-4-240.png" .format(CONST.ICONPATH)), 'CHECK NOW')
        self.performChecks.clicked.connect(self._performChecks)
        self.toolBar.addWidget(self.performChecks)

        return self.toolBar

    def _initCheckDock(self):
        self.dock = QDockWidget(self)
        self.dock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.dock.setWindowTitle('{} Sanity Checks:'.format(self.state))
        self.dockWidget = QWidget()
        self.dock.setWidget(self.dockWidget)
        self.dockLayout = QVBoxLayout(self.dockWidget)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock)
        self.dock.setMinimumWidth(150)

        if not hasattr(self, 'buttonLayout'):
            self.buttonLayout = QHBoxLayout(self)
            self.endableAll = QPushButton('Enable All')
            self.endableAll.clicked.connect(partial(self.toggleCheckBoxes, True))
            self.disableAll = QPushButton('disable All')
            self.disableAll.clicked.connect(partial(self.toggleCheckBoxes, False))
            self.buttonLayout.addWidget(self.endableAll)
            self.buttonLayout.addWidget(self.disableAll)
            self.dockLayout.addLayout(self.buttonLayout)

        self.dockLayout.addStretch(1)

    def _initChecksPassed(self):
        self.dockStatus = QDockWidget(self)
        self.dockStatus.setFeatures(QDockWidget.NoDockWidgetFeatures)

        self.dockStatusWidget = QWidget()
        self.dockStatus.setWidget(self.dockStatusWidget)
        self.dockStatusLayout = QHBoxLayout(self.dockStatusWidget)

        self.failedGrpBox = QGroupBox(self)
        self.failedGrpBox.setStyleSheet("QGroupBox{border: 1px solid gray; border-radius: 9px;}")
        self.failedGrpBox.setTitle('Failed:')
        self.failedGrpBoxLayout = QVBoxLayout(self.failedGrpBox)

        self.failedList = QListWidget(self)
        self.failedList.setEnabled(False)
        self.failedList.setMaximumWidth(150)
        self.failedList.itemClicked.connect(self._switchTabs)

        self.failedGrpBoxLayout.addWidget(self.failedList)

        self.passedGrpBox = QGroupBox(self)
        self.passedGrpBox.setTitle('Passed:')
        self.passedGrpBox.setStyleSheet("QGroupBox{border: 1px solid gray; border-radius: 9px;}")
        self.passedGrpBoxLayout = QVBoxLayout(self.passedGrpBox)
        self.passedList = QListWidget(self)
        self.passedList.setEnabled(False)
        self.passedList.setMaximumWidth(150)

        self.passedGrpBoxLayout.addWidget(self.passedList)

        self.dockStatusLayout.addWidget(self.passedGrpBox)
        self.dockStatusLayout.addWidget(self.failedGrpBox)

        self.addDockWidget(Qt.LeftDockWidgetArea, self.dockStatus)
        self.dockStatus.setMaximumWidth(300)

    def toggleCheckBoxes(self, val = False):
        if self.checkBoxes:
            for eachCbx in self.checkBoxes:
                eachCbx.setChecked(val)

    def _initCheckBoxes(self, stateCB = None):
        myPath = os.path.realpath(__file__)
        myPath = myPath.split(os.path.sep)
        myPath = "\\".join(myPath[:-1])
        filePath = "%s\\lib\\CONFIG.yaml" % myPath
        self.config = self._readYAML(filePath)
        ## Clean the previous checkboxes from widget
        if self.checkBoxes:
            for eachCBox in self.checkBoxes:
                eachCBox.close()
                eachCBox = None
        self.checkBoxes = []

        ## CHeck to see if we're changing the list to a new one or not
        if stateCB:
            self.state = stateCB
            self.dock.setWindowTitle('%s Sanity Checks:' % self.state)

        ## Setup the list now
        self.checkLayout = QVBoxLayout(self)
        if self.state in self.config['checks'].keys():
            self.checkList = self.config['checks'][self.state]
            for eachCheck in self.checkList:
                self.radioButton = QRadioButton(eachCheck, self)
                self.radioButton.setObjectName(eachCheck)
                self.radioButton.setAutoExclusive(False)
                self.radioButton.setChecked(True)
                self.checkBoxes.extend([self.radioButton])
                self.checkLayout.addWidget(self.radioButton)

            self.dockLayout.addLayout(self.checkLayout)
        else:
            raise Exception ('Missing key in yaml file for %s' % self.stat)

    def _switchTabs(self):
        currentItem = self.failedList.currentItem().text()
        for eachWidget in self.reports:
            if eachWidget.objectName() == currentItem:
                self.tabWidget.setCurrentWidget(eachWidget)

    def _readYAML(self, filePath):
        f = open(filePath, "r")
        data = yaml.load(f)
        return data

    def _performChecks(self):
        data = sanity.sanityCheck()
        for widget in self.reports:
            self.tabWidget.removeWidget(widget)

        self.failedList.clear()
        self.passedList.clear()

        for eachRB in self.checkBoxes:
            if eachRB.isChecked():
                if eachRB.objectName() in data.keys():  ## The sanity name is in the dict from the checks
                    if data[eachRB.objectName()]:       ## We have valid failed data to process
                        self.failedList.setEnabled(True)
                        self.reportQL = ReportWindow(self, eachRB.objectName())
                        self.reportQL.addData(data[eachRB.objectName()])
                        index = self.tabWidget.addWidget(self.reportQL)#, eachRB.objectName())
                        self.failedList.addItem(eachRB.objectName())
                        self.reports.extend([self.reportQL])
                    else:
                        self.passedList.addItem(eachRB.objectName())



SEP = " |  | " ## Used in the listWidgets to make it easier to read the long names
class ReportWindow(QWidget):
    def __init__(self, parent = None, label = {}):
        QWidget.__init__(self, parent)
        self.label = label
        self.setWindowTitle(self.label)
        self.setObjectName(self.label)
        self.mainLayout = QVBoxLayout(self)

        self.data = {}

        self.__initMainLayout()

    def __initMainLayout(self):
        """
        Setup the mainLayout for the reporter window
        :return:
        """
        self.groupBox = QGroupBox(self)
        self.groupBox.setTitle('{} failed items:'.format(self.label))
        self.groupBox.setStyleSheet("QGroupBox{border: 1px solid gray; border-radius: 9px;} QGroupBox::title {subcontrol-origin: margin;left: 100px;padding: -5 3px 0 3px;}")

        self.groupBoxLayout = QVBoxLayout(self.groupBox)

        self.reportTree = QListWidget(self)
        self.reportTree.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self._initRCMenu()
        self.reportTree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.reportTree.customContextMenuRequested.connect(self.showRightClickMenu)
        self.reportTree.itemClicked.connect(partial(self.processItems, case = 'select'))

        self.groupBoxLayout.addWidget(self.reportTree)
        self.mainLayout.addWidget(self.groupBox)

    def addData(self, data = []):
        """
        Process the data into the report window
        :param data: list of items to add to the listWidget
        :type data: list
        :return:
        """
        self.reportTree.clear()
        #for eachItem in dataList:
        #    self.reportTree.addItem(eachItem)
        stash = data
        for eachD in data:
            ## Add the item with a cleaner more readable spacer than maya's default |
            self.reportTree.addItem(eachD.replace("|", SEP))

            ## Now check to see if there are any more to report with the same name such as duplicate items
            ## Basically easier to read in the treview
            for eachStsh in stash:
                if eachStsh != eachD:
                    if eachStsh.split("|")[-1] == eachD.split("|")[-1]:
                        self.reportTree.addItem(eachStsh.replace("|", SEP))
                        data.remove(eachStsh)
            ## Now add a little sep between em
            self.reportTree.addItem("-----")

    def processItems(self, sender = None, all = False, case = ''):
        cmds.select(clear = True)
        if not all:
            for eachItem in self.reportTree.selectedItems():
                if "-----" not in eachItem.text():
                    if case == 'select':
                        cmds.select(eachItem.text().replace(SEP, "|"), add = True)
                    elif case == 'delete':
                        cmds.delete(eachItem.text().replace(SEP, "|"))
        else:
            count = self.reportTree.count()
            toSel = []
            for x in range(count):
                if "-----" not in self.reportTree.item(x).text():
                    toSel.extend([self.reportTree.item(x).text()].replace(SEP, "|"))

            if case == 'select':
                cmds.select(toSel, r = True)
            elif case == 'delete':
                cmds.delete(toSel)

    def addSuffix(self, suffix = ''):
        for eachItem in self.reportTree.selectedItems():
            name = eachItem.text().replace(SEP, "|")
            cmds.rename(name, "{0}_{1}".format(name.split("|")[-1], suffix))

    def _initRCMenu(self):
        self.rightClickMenu = QMenu()
        self.rightClickMenu.setObjectName('Actions')
        self.rightClickMenu.setWindowTitle('Actions')

        self.selectAction = QAction('Select', self)
        self.selectAction.setIcon(QIcon("{}/iconmonstr-plus-1-240.png" .format(CONST.ICONPATH)))
        self.selectAction.triggered.connect(partial(self.processItems, case = 'select'))

        self.geoSuffixAction = QAction('Add geo suffix', self)
        self.geoSuffixAction.triggered.connect(partial(self.addSuffix, suffix = CONST.GEOMETRY_SUFFIX))

        self.grpSuffixAction = QAction('Add grp suffix', self)
        self.grpSuffixAction.triggered.connect(partial(self.addSuffix, suffix = CONST.GROUP_SUFFIX))

        self.deleteAction = QAction('Delete', self)
        self.deleteAction.setIcon(QIcon("{}/iconmonstr-trash-can-5-240.png" .format(CONST.ICONPATH)))
        self.deleteAction.triggered.connect(partial(self.processItems, case = 'delete'))

        self.rightClickMenu.addAction(self.selectAction)
        self.rightClickMenu.addSeparator()
        self.rightClickMenu.addAction(self.geoSuffixAction)
        self.rightClickMenu.addAction(self.grpSuffixAction)
        self.rightClickMenu.addSeparator()
        self.rightClickMenu.addAction(self.deleteAction)

    def showRightClickMenu(self, position):
        self.rightClickMenu.exec_(self.reportTree.viewport().mapToGlobal(position))
        self.rightClickMenu.show()