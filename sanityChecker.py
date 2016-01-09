"""
Created by James Dunlop
2016
Dependencies yaml
"""
import os, yaml, logging
from functools import partial
from PySide.QtCore import *
from PySide.QtGui import *
logger = logging.getLogger(__name__)
from python import sanity_lib as sanity
import python.sanity_lib.CONST as CONST
import maya.cmds as cmds
reload(CONST)
SEP = " |  | " ## Used in the listWidgets to make it easier to read the long names
reload(sanity)
## TODO add a feature to remove the 1 at the end of the badly numbered items
## TODO Fix the bug in shape name checking that geo_Shape shows up and needs cleaning!

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
        ic = QIcon("{}/iconmonstr-cube-11-240.png".format(CONST.ICONPATH))
        self.mdlAction.setIcon(ic)
        self.mdlAction.setToolTip('Set checks for modeling dept')
        self.mdlAction.triggered.connect(partial(self._initCheckBoxes, stateCB = 'mdl'))

        self.rigAction = QAction('rig', self)
        ic = QIcon("{}/iconmonstr-magic-6-240.png".format(CONST.ICONPATH))
        self.rigAction.setIcon(ic)
        self.rigAction.setToolTip('Set checks for rig dept')
        self.rigAction.triggered.connect(partial(self._initCheckBoxes, stateCB = 'rig'))

        self.animAction = QAction('anim', self)
        ic = QIcon("{}/iconmonstr-direction-10-240.png".format(CONST.ICONPATH))
        self.animAction.setIcon(ic)
        self.animAction.setToolTip('Set checks for anim dept')
        self.animAction.triggered.connect(partial(self._initCheckBoxes, stateCB = 'anim'))

        self.lightAction = QAction('light', self)
        ic = QIcon("{}/iconmonstr-light-bulb-16-240.png".format(CONST.ICONPATH))
        self.lightAction.setIcon(ic)
        self.lightAction.setToolTip('Set checks for lighting dept')
        self.lightAction.triggered.connect(partial(self._initCheckBoxes, stateCB = 'light'))

        self.toolBar.addAction(self.mdlAction)
        self.toolBar.addAction(self.rigAction)
        self.toolBar.addAction(self.animAction)
        self.toolBar.addAction(self.lightAction)
        self.toolBar.addSeparator()

        self.performChecks = QPushButton(QIcon("{}/iconmonstr-log-out-4-240.png".format(CONST.ICONPATH)), 'CHECK NOW')
        self.performChecks.clicked.connect(self._performChecks)
        self.toolBar.addWidget(self.performChecks)

        self.space01 = QWidget(self)
        self.space01.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.toolBar.addWidget(self.space01)

        self.toolBar.addSeparator()
        self.changeConfigAction = QPushButton('Edit Config', self)
        ic = QIcon("{}/iconmonstr-gear-11-240.png".format(CONST.ICONPATH))
        self.changeConfigAction.setIcon(ic)
        self.changeConfigAction.setToolTip('Change the config settings')
        self.changeConfigAction.clicked.connect(self._editConfig)
        self.toolBar.addWidget(self.changeConfigAction)

        return self.toolBar

    def _editConfig(self):
        self.configWin = ConfigUI()
        self.configWin.show()

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
        self.config = loadConfig()
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
        if self.state in self.config['activechecks'].keys():
            self.checkList = self.config['activechecks'][self.state]
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
        self.parent = parent
        self.label = label
        self.setWindowTitle(self.label)
        self.setObjectName(self.label)
        self.mainLayout = QVBoxLayout(self)
        self.config = loadConfig()
        self.data = {}
        self.__initMainLayout()

        self.setFocus()

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

    def _initRCMenu(self):
        self.rightClickMenu = QMenu()
        self.rightClickMenu.setObjectName('Actions')
        self.rightClickMenu.setWindowTitle('Actions')

        ################################################################################################################
        ################################################################################################################
        ## ADD CUSTOM ACTIONS FOR CUSTOM SANITY CHECKS HERE
        ## Define the custom actions now that the config will query each check to show or hide based on the
        ## type of check done
        self.geoSuffixAction = QAction('Add \"_{}\" suffix'.format(CONST.GEOMETRY_SUFFIX), self)
        self.geoSuffixAction.setObjectName('AddGeoSuffix')
        self.geoSuffixAction.setIcon(QIcon("{}/iconmonstr-plus-1-240.png".format(CONST.ICONPATH)))
        self.geoSuffixAction.triggered.connect(partial(self.addSuffix, suffix = CONST.GEOMETRY_SUFFIX))

        self.grpSuffixAction = QAction('Add \"_{}\" suffix'.format(CONST.GROUP_SUFFIX), self)
        self.grpSuffixAction.setObjectName('AddGrpSuffix')
        self.grpSuffixAction.setIcon(QIcon("{}/iconmonstr-plus-1-240.png".format(CONST.ICONPATH)))
        self.grpSuffixAction.triggered.connect(partial(self.addSuffix, suffix = CONST.GROUP_SUFFIX))

        self.crvSuffixAction = QAction('Add \"_{}\" suffix'.format(CONST.NURBSCRV_SUFFIX), self)
        self.crvSuffixAction.setObjectName('AddCrvSuffix')
        self.crvSuffixAction.setIcon(QIcon("{}/iconmonstr-plus-1-240.png".format(CONST.ICONPATH)))
        self.crvSuffixAction.triggered.connect(partial(self.addSuffix, suffix = CONST.NURBSCRV_SUFFIX))

        self.renameAction = QAction('Rename', self)
        self.renameAction.setObjectName('rename')
        self.renameAction.setIcon(QIcon("{}/iconmonstr-tumblr-4-240.png".format(CONST.ICONPATH)))
        self.renameAction.triggered.connect(partial(self.renamePopUpUI))

        self.removeShapesAction = QAction('Remove Shapes from List', self)
        self.removeShapesAction.setObjectName('removeShapes')
        self.removeShapesAction.setIcon(QIcon("{}/iconmonstr-tumblr-4-240.png".format(CONST.ICONPATH)))
        self.removeShapesAction.triggered.connect(partial(self.removeFromList, '{}Shape'.format(CONST.GEOMETRY_SUFFIX)))

        self.actions = [self.geoSuffixAction, self.grpSuffixAction, self.crvSuffixAction, self.renameAction, self.removeShapesAction]
        ################################################################################################################
        ################################################################################################################

        ## DEFAULT Right click menu actions
        self.deleteAction = QAction('Delete', self)
        self.deleteAction.setIcon(QIcon("{}/iconmonstr-trash-can-5-240.png".format(CONST.ICONPATH)))
        self.deleteAction.triggered.connect(partial(self.processItems, case = 'delete'))

        ## Add the custom menu items to this report view
        actionsToDisplay = self.config["rcMenu"][self.label]
        for eachAction in self.actions:
            if eachAction.objectName() in actionsToDisplay:
                self.rightClickMenu.addAction(eachAction)

        ## Add the defaults now
        self.rightClickMenu.addSeparator()
        self.rightClickMenu.addAction(self.deleteAction)

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
        cmds.undoInfo(openChunk = True)
        cmds.select(clear = True)
        if not all:
            for eachItem in self._getSelItems():
                if case == 'select':
                    cmds.select(eachItem.text().replace(SEP, "|"), add = True, ne = True)
                elif case == 'delete':
                    cmds.delete(eachItem.text().replace(SEP, "|"))
        else:
            count = self.reportTree.count()
            items = []
            for x in range(count):
                if "-----" not in self.reportTree.item(x).text():
                    items.extend([self.reportTree.item(x).text()].replace(SEP, "|"))

            if case == 'select':
                cmds.select(items, r = True, ne = True)
            elif case == 'delete':
                cmds.delete(items)
        cmds.undoInfo(closeChunk = True)

    def addSuffix(self, suffix = ''):
        cmds.undoInfo(openChunk = True)
        cmds.select(clear = True)
        for eachItem in self._getSelItems():
            name = eachItem.text().replace(SEP, "|")
            cmds.rename(name, "{0}_{1}".format(name.split("|")[-1], suffix))
        cmds.undoInfo(closeChunk = True)
        self.parent._performChecks()

    def renamePopUpUI(self):
        self.renameWidget = QWidget(None)
        self.renameWidget.setObjectName('RenameWindow')
        self.renameWidget.setWindowTitle('Object(s) Renamer Window')
        self.renameWidgetMainLayout = QVBoxLayout(self.renameWidget)
        self.usage = QLabel(self)
        msg = 'Usage:\n' \
              'If you have a mutli selection, you can  use # to set the place where you want the padding.\n' \
              'eg: TestName#_geo will result in TestName00_geo TestName01_geo'
        self.usage.setText(msg)
        self.renameLayout = QHBoxLayout(self)
        self.renameLabel = QLabel('RenameTo:')
        self.renameInput = QLineEdit()
        self.renameInput.setToolTip('If you have a mutli selection, you can  use # to set the place where you want the padding.\neg: TestName#_geo will result in TestName00_geo TestName01_geo')
        self.renameInput.returnPressed.connect(self.renameItems)
        self.renameInput.returnPressed.connect(partial(self.renameWidget.close))

        self.renameLayout.addWidget(self.renameLabel)
        self.renameLayout.addWidget(self.renameInput)

        self.renameWidgetMainLayout.addWidget(self.usage)
        self.renameWidgetMainLayout.addLayout(self.renameLayout)
        self.renameWidget.show()
        self.renameWidget.resize(600, 100)
        self.renameWidget.setFocus()

    def _getSelItems(self):
        items = [item for item in self.reportTree.selectedItems() if item.text() != '-----']
        return items

    def renameItems(self,):
        if not hasattr(self, 'renameWidget'):
            return

        renameTo = self.renameInput.text()
        if renameTo:
            cmds.undoInfo(openChunk = True)
            count = len(self._getSelItems())
            if count > 1:
                items = self._getSelItems()
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
            cmds.undoInfo(closeChunk = True)
        else:
            logger.info('Please type a name?!')

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

    def showRightClickMenu(self, position):
        self.rightClickMenu.exec_(self.reportTree.viewport().mapToGlobal(position))
        self.rightClickMenu.show()


class CheckLists(QWidget)
    ##TODO Change this layout to be 2 list boxes that you can move items over to valid or not as I can se this list becoming stupidly long.
    def __init__(self, parent = None, label = "", data = {}):
        QWidget.__init__(self, parent)
        self.label = label
        self.data = data
        self.setWindowTitle(self.label)
        self.setObjectName(self.label)
        self.mainLayout = QVBoxLayout(self)

        self.groupBox = QGroupBox(self)
        self.groupBox.setTitle(self.label)
        self.groupBoxLayout = QHBoxLayout(self.groupBox)

        self.baseList = QListWidget(self)
        self.activeList = QListWidget(self)

        self.buttonLayout = QVBoxLayout(self)
        self.moveToActiveButton = QPushButton(QIcon('{}\\.png'.format(CONST.ICONPATH)))
        self.moveToBaseButton = QPushButton(QIcon('{}\\.png'.format(CONST.ICONPATH)))

        self.groupBoxLayout.addWidget(self.baseList)
        self.groupBoxLayout.addLayout(self.buttonLayout)
        self.groupBoxLayout.addWidget(self.activeList)

        self.mainLayout.addWidget(self.groupBox)

    def _addData(self):
        pass

    def _addToActiveList(self):
        pass

    def _removeFromActiveList(self):
        pass

class ConfigUI(QWidget):
    ##TODO Change this layout to be 2 list boxes that you can move items over to valid or not as I can se this list becoming stupidly long.
    def __init__(self, parent = None, label = "Config"):
        QWidget.__init__(self, parent)
        self.label = label
        self.setWindowTitle(self.label)
        self.setObjectName(self.label)
        self.mainLayout = QVBoxLayout(self)
        self.config = loadConfig()
        self.configData = {}
        self.__initMainLayout()
        self._initRCMenu()

    def __initMainLayout(self):
        """
        Setup the mainLayout for the UI
        :return:
        """

        self.checksLayout = QVBoxLayout(self)
        checks = self.config['activechecks']
        for checkDept, checkList in checks.items():
            self.configData[checkDept] = {}
            self.deptGrpBox = QGroupBox(self)
            self.deptGrpBox.setObjectName('{}GroupBox'.format(checkDept))
            self.deptGrpBox.setTitle(checkDept)

            self.deptGrpBoxLayout = QGridLayout(self.deptGrpBox)
            self.deptGrpBox.setContextMenuPolicy(Qt.CustomContextMenu)
            self.deptGrpBox.customContextMenuRequested.connect(self.showRightClickMenu)

            self.validChecks = QListWidget(self)
            self.activeChecks = QListWidget(self)

            for eachCheck in self.config["checkList"]:
                self.validChecks.addItem(eachCheck)

            for eachItem in checkList:
                self.activeChecks.addItem(eachItem)

            self.deptGrpBoxLayout.addWidget(self.validChecks)
            self.deptGrpBoxLayout.addWidget(self.activeChecks)

            ## Now add the groupbox to the layout
            self.checksLayout.addWidget(self.deptGrpBox)

        ## Add a check to a dept or all depts at once
        self.mainLayout.addLayout(self.checksLayout)

        self.saveButton = QPushButton('Save')
        self.saveButton.clicked.connect(self.saveConfig)
        self.cancelButton = QPushButton('Close')
        self.cancelButton.clicked.connect(self.close)

        self.mainLayout.addWidget(self.saveButton)
        self.mainLayout.addWidget(self.cancelButton)

    def _initRCMenu(self):
        self.rightClickMenu = QMenu()
        self.rightClickMenu.setObjectName('CheckMenu')
        self.rightClickMenu.setWindowTitle('CheckMenu')

        ## DEFAULT Right click menu actions
        self.selAllAction = QAction('Select All', self)
        self.selAllAction.setIcon(QIcon("{}/iconmonstr-checkbox-10-240.png".format(CONST.ICONPATH)))
        self.selAllAction.triggered.connect(partial(self.selAll, True))

        self.deselAllAction = QAction('DeSelect All', self)
        self.deselAllAction.setIcon(QIcon("{}/iconmonstr-minus-4-240.png".format(CONST.ICONPATH)))
        self.deselAllAction.triggered.connect(partial(self.selAll, False))

        ## Add the defaults now
        self.rightClickMenu.addSeparator()
        self.rightClickMenu.addAction(self.selAllAction)
        self.rightClickMenu.addAction(self.deselAllAction)

    def showRightClickMenu(self, position):
        cursor = QCursor()
        self.rightClickMenu.exec_(cursor.pos())
        self.rightClickMenu.show()

    def saveConfig(self):
        ## Process checks for which are on or off
        data = {}
        for key, var in self.config.items():
            data[key] = var

        for checkDept, radioBoxes in self.configData.items():
            validChecks = []
            for checkName, radioBox in radioBoxes.items():
                if radioBox.isChecked():
                    validChecks.append(checkName)

            data['activechecks'][checkDept] = validChecks

        _dumpYAML(data)
        print 'Config updated successfully.'
        self.close()

    def selAll(self, val = True):
        cursor = QCursor()
        try:
            deptName = [w.objectName() for w in widgets_at(cursor.pos()) if 'GroupBox' in w.objectName()][0].replace('GroupBox', '')
        except IndexError:
            print 'Failed to list widet. Please right click again.'
        for checkDept, radioBoxes in self.configData.items():
            if checkDept == deptName:
                for checkName, radioBox in radioBoxes.items():
                    radioBox.setChecked(val)



################### FUNCS
def loadConfig():
    configPath = os.path.realpath(__file__)
    configPath = configPath.split(os.path.sep)
    configPath = "\\".join(configPath[:-1])
    filePath = "%s\\CONFIG.yaml" % configPath
    return _readYAML(filePath)

def _readYAML(filePath):
    f = open(filePath, "r")
    data = yaml.load(f)
    return data

def _dumpYAML(data):
    configPath = os.path.realpath(__file__)
    configPath = configPath.split(os.path.sep)
    configPath = "\\".join(configPath[:-1])
    filePath = "%s\\CONFIG.yaml" % configPath
    with open(filePath, 'w') as outfile:
        outfile.write(yaml.dump(data))

def widgets_at(pos):
    """Return ALL widgets at `pos`
    Arguments:
        pos (QPoint): Position at which to get widgets
    """
    widgets = []
    widget_at = qApp.widgetAt(pos)
    while widget_at:
        widgets.append(widget_at)
        # Make widget invisible to further enquiries
        widget_at.setAttribute(Qt.WA_TransparentForMouseEvents)
        widget_at = qApp.widgetAt(pos)
    # Restore attribute
    for widget in widgets:
        widget.setAttribute(Qt.WA_TransparentForMouseEvents, False)
    return widgets