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
SEP = " |  | " ## Used in the listWidgets to make it easier to read the long names


class SanityUI(QMainWindow):
    def __init__(self, parent = None):
        QMainWindow.__init__(self, parent)
        self.setWindowTitle('Sanity Check')
        self.setObjectName('Sanity Check')
        self.checkBoxes = []
        self.reports = []
        ## Load the config file from disk
        self.config = loadConfig()

        ## Set the intial checking list
        self.state = 'rig'
        ## Now INIT the ui
        self._initCheckDock()
        self._initCheckBoxes()
        self._initChecksPassed()

        ## Create the center widget stacked info report stuff
        self.tabWidget = QStackedWidget(self)
        self.setCentralWidget(self.tabWidget)

        ## Add the toolbar to the top
        self.addToolBar(self._initToolBar())

        ## Final layout stuff
        self.setDockNestingEnabled(True)
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
        self.dockLayout = QGridLayout(self.dockWidget)
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
            self.dockLayout.addLayout(self.buttonLayout, 0, 0)

    def _initCheckBoxes(self, stateCB = None):
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

            self.dockLayout.addLayout(self.checkLayout, 1, 0)
            self.checkLayout.addStretch(1)
        else:
            raise Exception ('Missing key in yaml file for %s' % self.stat)

        self.dockLayout.rowStretch(3)

    def _initChecksPassed(self):
        self.dockStatus = QDockWidget(self)
        self.dockStatus.hide()
        self.dockStatus.setWindowTitle('Check Results')
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
        self.tabifyDockWidget(self.dock, self.dockStatus)
        self.splitDockWidget(self.dock, self.dockStatus, Qt.Horizontal)

    def toggleCheckBoxes(self, val = False):
        if self.checkBoxes:
            for eachCbx in self.checkBoxes:
                eachCbx.setChecked(val)

    def _switchTabs(self):
        currentItem = self.failedList.currentItem().text()
        for eachWidget in self.reports:
            if eachWidget.objectName() == currentItem:
                self.tabWidget.setCurrentWidget(eachWidget)

    def _performChecks(self):
        data = sanity.sanityCheck()
        for widget in self.reports:
            self.tabWidget.removeWidget(widget)

        self.failedList.clear()
        self.passedList.clear()
        self.dockStatus.show()

        self.failed = False
        for eachRB in self.checkBoxes:
            if eachRB.isChecked():
                if eachRB.objectName() in data.keys():  ## The sanity name is in the dict from the checks
                    if data[eachRB.objectName()]:       ## We have valid failed data to process
                        self.failed = True
                        self.failedList.setEnabled(True)
                        self.reportQL = ReportWindow(self, eachRB.objectName())
                        self.reportQL.addData(data[eachRB.objectName()])
                        index = self.tabWidget.addWidget(self.reportQL)#, eachRB.objectName())
                        self.failedList.addItem(eachRB.objectName())
                        self.reports.extend([self.reportQL])
                    else:
                        self.passedList.addItem(eachRB.objectName())

        if not self.failed:
            self.allPassedWidget = QWidget(self)
            self.allPassedLayout = QVBoxLayout(self.allPassedWidget)
            self.passed = QPixmap("{}/iconmonstr-checkbox-10-240.png".format(CONST.ICONPATH))
            self.passed.scaled(800, 600, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)

            self.passedLabel = QSplashScreen(self.passed)

            self.allPassedLayout.addWidget(self.passedLabel)

            self.tabWidget.addWidget(self.allPassedWidget)

            self.reports.extend([self.allPassedWidget])



class ReportWindow(QWidget):
    def __init__(self, parent = None, label = {}):
        QWidget.__init__(self, parent)
        self.label = label
        self.setWindowTitle(self.label)
        self.setObjectName(self.label)
        self.mainLayout = QVBoxLayout(self)
        self.config = loadConfig()
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

    def renamePopUpUI(self):
        self.renameWidget = QWidget(None)
        self.renameLayout = QHBoxLayout(self.renameWidget)
        self.renameLabel = QLabel('RenameTo:')

        self.renameInput = QLineEdit()
        self.renameInput.setToolTip('If you have a mutli selection, you can  use # to set the place where you want the padding.\neg: TestName#_geo will result in TestName00_geo TestName01_geo')
        self.renameInput.returnPressed.connect(self.renameItems)
        self.renameInput.returnPressed.connect(partial(self.renameWidget.close))

        self.renameLayout.addWidget(self.renameLabel)
        self.renameLayout.addWidget(self.renameInput)
        self.renameWidget.show()

    def renameItems(self,):
        if not hasattr(self, 'renameWidget'):
            return

        renameTo = self.renameInput.text()
        if renameTo:
            count = len(self.reportTree.selectedItems())
            if count > 1:
                items = [item for item in self.reportTree.selectedItems()]
                for x in range(count):
                    curItem = items[x].text().replace(SEP, "|")
                    if "#" in renameTo:
                        cmds.rename(curItem, "{0}".format(renameTo.replace("#", "{0:02d}".format(x))))
                    else:
                        cmds.rename(curItem, "{0}{1:02d}".format(renameTo, x))
            else:
                name = self.reportTree.currentItem().text().replace(SEP, "|")
                if "#" in renameTo:
                    cmds.rename(name, renameTo.replace("#", "00"))
                else:
                    cmds.rename(name, renameTo)
        else:
            logger.info('No name set.')

    def removeFromList(self, searchString = ''):
        ##TODO this isn't working as intended the resulting addData is all over the place :(
        count = self.reportTree.count()
        treeWidgets = []
        for x in range(count):
            if searchString not in self.reportTree.item(x).text() and self.reportTree.item(x).text() != "-----":
                if self.reportTree.item(x).text().replace(SEP, "|") not in treeWidgets:
                    treeWidgets.extend([self.reportTree.item(x).text().replace(SEP, "|")])
        self.reportTree.clear()
        self.addData(treeWidgets)

    def _initRCMenu(self):
        self.rightClickMenu = QMenu()
        self.rightClickMenu.setObjectName('Actions')
        self.rightClickMenu.setWindowTitle('Actions')

        ################################################################################################################
        ################################################################################################################
        ## ADD CUSTOM ACTIONS FOR CUSTOM SANITY CHECKS HERE
        ## Define the custom actions now that the config will query each check to show or hide based on the type of check done
        self.geoSuffixAction = QAction('Add geo suffix', self)
        self.geoSuffixAction.setObjectName('AddGeoSuffix')
        self.geoSuffixAction.setIcon(QIcon("{}/iconmonstr-plus-1-240.png".format(CONST.ICONPATH)))
        self.geoSuffixAction.triggered.connect(partial(self.addSuffix, suffix = CONST.GEOMETRY_SUFFIX))

        self.grpSuffixAction = QAction('Add grp suffix', self)
        self.grpSuffixAction.setObjectName('AddGrpSuffix')
        self.grpSuffixAction.setIcon(QIcon("{}/iconmonstr-plus-1-240.png".format(CONST.ICONPATH)))
        self.grpSuffixAction.triggered.connect(partial(self.addSuffix, suffix = CONST.GROUP_SUFFIX))

        self.renameAction = QAction('Rename', self)
        self.renameAction.setObjectName('rename')
        self.renameAction.setIcon(QIcon("{}/iconmonstr-tumblr-4-240.png".format(CONST.ICONPATH)))
        self.renameAction.triggered.connect(partial(self.renamePopUpUI))

        self.removeShapesAction = QAction('Remove Shapes from List', self)
        self.removeShapesAction.setObjectName('removeShapes')
        self.removeShapesAction.setIcon(QIcon("{}/iconmonstr-tumblr-4-240.png".format(CONST.ICONPATH)))
        self.removeShapesAction.triggered.connect(partial(self.removeFromList, '{}Shape'.format(CONST.GEOMETRY_SUFFIX)))

        self.actions = [self.geoSuffixAction, self.grpSuffixAction, self.renameAction, self.removeShapesAction]
        ################################################################################################################
        ################################################################################################################

        ## DEFAULT Right click menu actions
        self.deleteAction = QAction('Delete', self)
        self.deleteAction.setIcon(QIcon("{}/iconmonstr-trash-can-5-240.png" .format(CONST.ICONPATH)))
        self.deleteAction.triggered.connect(partial(self.processItems, case = 'delete'))

        ## Add the custom menu items to this report view
        actionsToDisplay = self.config["rcMenu"][self.label]
        for eachAction in self.actions:
            if eachAction.objectName() in actionsToDisplay:
                self.rightClickMenu.addAction(eachAction)

        ## Add the defaults now
        self.rightClickMenu.addSeparator()
        self.rightClickMenu.addAction(self.deleteAction)

    def showRightClickMenu(self, position):
        self.rightClickMenu.exec_(self.reportTree.viewport().mapToGlobal(position))
        self.rightClickMenu.show()


################### FUNCS
def loadConfig():
    myPath = os.path.realpath(__file__)
    myPath = myPath.split(os.path.sep)
    myPath = "\\".join(myPath[:-1])
    filePath = "%s\\lib\\CONFIG.yaml" % myPath
    return _readYAML(filePath)

def _readYAML(filePath):
    f = open(filePath, "r")
    data = yaml.load(f)
    return data