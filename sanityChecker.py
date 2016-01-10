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
import python.sanity_lib.sanity as sanity
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
        self.setDockNestingEnabled(False)
        self.setTabPosition(Qt.LeftDockWidgetArea, QTabWidget.North)
        self.resize(1200, 600)

        # for eachChild in self.children():
        #     if type(eachChild) == QTabBar:
        #         eachChild.currentChanged.connect(self._tabChange)

    def _initToolBar(self):
        self.toolBar = QToolBar(self)
        self.toolBar.setFloatable(False)
        self.toolBar.setMovable(False)
        self.toolBar.setAllowedAreas(Qt.TopToolBarArea)

        buttonConfig = self.config['buttons']
        for buttonName, buttonDict in buttonConfig.items():
            self.action = QAction(buttonName, self)
            ic = QIcon("{}/{}.png".format(CONST.ICONPATH, buttonDict['icon']))
            self.action.setIcon(ic)
            self.action.setToolTip(buttonDict['toolTip'])
            self.action.triggered.connect(partial(self._initCheckBoxes, stateCB = buttonName))
            self.toolBar.addAction(self.action)

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
        self.checksDock = QDockWidget(self)
        self.checksDock.setMinimumWidth(300)
        self.checksDock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.checksDock.setWindowTitle('{} Sanity Checks:'.format(self.state))
        self.dockWidget = QWidget()
        self.checksDock.setWidget(self.dockWidget)
        self.dockLayout = QGridLayout(self.dockWidget)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.checksDock)

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
        self.cbConfigBox = QGroupBox(self)
        self.cbConfigBox.setTitle("Sanity Checks:")
        self.cbConfigBox.setStyleSheet("QGroupBox{border-radius: 15px; border: 2px solid gray; font-size: 18px; font-weight: bold;margin-top: 5ex;} QGroupBox::title{padding: -50 1 1 1;}")
        ## Clean the previous checkboxes from widget
        if self.checkBoxes:
            for eachCBox in self.checkBoxes:
                eachCBox.close()
                eachCBox = None
        self.checkBoxes = []

        ## CHeck to see if we're changing the list to a new one or not
        if stateCB:
            self.state = stateCB
            self.checksDock.setWindowTitle('%s Sanity Checks:' % self.state)

        ## Setup the list now
        self.checkLayout = QVBoxLayout(self.cbConfigBox)
        if self.state in self.config['activechecks'].keys():
            self.checkList = self.config['activechecks'][self.state]
            for eachCheck in self.checkList:
                self.radioButton = QRadioButton(eachCheck, self)
                self.radioButton.setObjectName(eachCheck)
                self.radioButton.setAutoExclusive(False)
                self.radioButton.setChecked(True)
                self.checkBoxes.extend([self.radioButton])
                self.checkLayout.addWidget(self.radioButton)

            self.dockLayout.addWidget(self.cbConfigBox, 1, 0)
            self.checkLayout.addStretch(1)
        else:
            raise Exception ('Missing key in yaml file for %s' % self.stat)

        self.dockLayout.rowStretch(3)

    def _initChecksPassed(self):
        self.checkResultsDock = QDockWidget(self)
        self.checkResultsDock.setMinimumWidth(300)
        self.checkResultsDock.hide()
        self.checkResultsDock.setWindowTitle('Check Results')
        self.checkResultsDock.setFeatures(QDockWidget.NoDockWidgetFeatures)

        self.checkResultsDockWidget = QWidget()
        self.checkResultsDock.setWidget(self.checkResultsDockWidget)
        self.checkResultsDockLayout = QHBoxLayout(self.checkResultsDockWidget)

        self.failedGrpBox = QGroupBox(self)
        self.failedGrpBox.setStyleSheet("QGroupBox{border-radius: 15px; border: 2px solid gray; font-size: 18px; font-weight: bold;margin-top: 5ex;} QGroupBox::title{padding: -50 1 1 1;}")
        self.failedGrpBox.setTitle('Failed:')
        self.failedGrpBoxLayout = QVBoxLayout(self.failedGrpBox)

        self.failedList = QListWidget(self)
        self.failedList.setEnabled(False)
        self.failedList.itemClicked.connect(self._switchTabs)

        self.failedGrpBoxLayout.addWidget(self.failedList)

        self.passedGrpBox = QGroupBox(self)
        self.passedGrpBox.setTitle('Passed:')
        self.passedGrpBox.setStyleSheet("QGroupBox{border-radius: 15px; border: 2px solid gray; font-size: 18px; font-weight: bold;margin-top: 5ex;} QGroupBox::title{padding: -50 1 1 1;}")
        self.passedGrpBoxLayout = QVBoxLayout(self.passedGrpBox)
        self.passedList = QListWidget(self)
        self.passedList.setEnabled(False)

        self.passedGrpBoxLayout.addWidget(self.passedList)

        self.checkResultsDockLayout.addWidget(self.passedGrpBox)
        self.checkResultsDockLayout.addWidget(self.failedGrpBox)

        self.addDockWidget(Qt.LeftDockWidgetArea, self.checkResultsDock)
        self.tabifyDockWidget(self.checksDock, self.checkResultsDock)

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
        self.checkResultsDock.show()

        self.failed = False
        for eachRB in self.checkBoxes:
            if eachRB.isChecked():
                if eachRB.objectName() in data.keys():  ## The sanity name is in the dict from the checks
                    if data[eachRB.objectName()]:       ## We have valid failed data to process
                        self.failed = True
                        self.failedList.setEnabled(True)
                        self.reportQL = ReportWindow(self, eachRB.objectName())
                        self.reportQL.addData(data[eachRB.objectName()])
                        index = self.tabWidget.addWidget(self.reportQL)
                        self.failedList.addItem(eachRB.objectName())
                        self.reports.extend([self.reportQL])
                    else:
                        self.passedList.addItem(eachRB.objectName())

        if not self.failed:
            self.allPassedWidget = QWidget(self)
            self.allPassedLayout = QHBoxLayout(self.allPassedWidget)

            self.passed = QPixmap("{}/iconmonstr-checkbox-10-240.png".format(CONST.ICONPATH))
            self.passed.scaled(800, 600, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
            self.passedLabel = QSplashScreen(self.passed)
            self.allPassedLayout.addWidget(self.passedLabel)

            self.tabWidget.addWidget(self.allPassedWidget)
            self.reports.extend([self.allPassedWidget])

        self.checkResultsDock.show()
        self.checkResultsDock.raise_()
        self.checkResultsDock.setFixedWidth(300)
        self.checksDock.setFixedWidth(300)



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
        self.groupBox.setTitle('{}:'.format(self.label))
        self.groupBox.setStyleSheet("QGroupBox{border-radius: 15px; border: 2px solid gray; font-size: 18px; font-weight: bold;margin-top: 5ex;} QGroupBox::title{padding: -50 1 1 1;}")
        self.groupBoxLayout = QVBoxLayout(self.groupBox)

        self.reportTree = QListWidget(self)
        self.reportTree.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self._initRCMenu()
        ## Set the rick click menus now
        self.reportTree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.reportTree.customContextMenuRequested.connect(self.showRightClickMenu)
        self.reportTree.itemClicked.connect(partial(self.processItems, case = 'select'))

        self.groupBoxLayout.addWidget(self.reportTree)
        self.mainLayout.addWidget(self.groupBox)

    def _initRCMenu(self):
        """
        THis is a customizable area that relates to the config.
        In the config.yaml file there is a rightClickCheckSubMenus entry you can edit
        Each report window for a sanity check can have a special right click added this way for cleaning the errors found.
        Each of the cleanups are methods in this class for now.
        :return:
        """
        self.rightClickMenu = QMenu()
        self.rightClickMenu.setObjectName('Actions')
        self.rightClickMenu.setWindowTitle('Actions')
        ################################################################################################################
        # START EDITING HERE
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

        self.deleteCHAction = QAction('Delete ConsHist', self)
        self.deleteCHAction.setObjectName('constructionHistory')
        self.deleteCHAction.setIcon(QIcon("{}/iconmonstr-trash-can-5-240.png".format(CONST.ICONPATH)))
        self.deleteCHAction.triggered.connect(partial(self.processItems, case = 'deleteCH'))

        self.removeShapesAction = QAction('Remove Shapes from List', self)
        self.removeShapesAction.setObjectName('removeShapes')
        self.removeShapesAction.setIcon(QIcon("{}/iconmonstr-eye-3-icon-256.png".format(CONST.ICONPATH)))
        self.removeShapesAction.triggered.connect(partial(self.removeFromList, '{}Shape'.format(CONST.GEOMETRY_SUFFIX)))

        self.actions = [self.geoSuffixAction, self.grpSuffixAction, self.crvSuffixAction, self.renameAction,
                        self.removeShapesAction, self.deleteCHAction]
        ################################################################################################################
        # STOP EDITING HERE
        ################################################################################################################
        ## DEFAULT Right click menu actions
        self.deleteAction = QAction('Delete', self)
        self.deleteAction.setIcon(QIcon("{}/iconmonstr-trash-can-5-240.png".format(CONST.ICONPATH)))
        self.deleteAction.triggered.connect(partial(self.processItems, case = 'delete'))

        ## Add the custom menu items to this report view
        actionsToDisplay = self.config["rightClickCheckSubMenus"][self.label]
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
                elif case == 'deleteCH':
                    cmds.delete(eachItem.text().replace(SEP, "|"), ch = True)
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
            elif case == 'deleteCH':
                cmds.delete(items, ch = True)

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



class ConfigCheckLists(QWidget):
    def __init__(self, parent = None, label = "", allChecks_List = {}, activeCheck_List = {}):
        QWidget.__init__(self, parent)
        self.label = label
        self.allChecks_List = allChecks_List
        self.activeChecks_List = activeCheck_List

        ## Set base widget up
        self.setWindowTitle(self.label)
        self.setObjectName(self.label)
        self.mainLayout = QVBoxLayout(self)

        ## Initialize the UI
        self._initUI()
        ## Add the data to the list widgets
        self._addData()

    def _initUI(self):
        self.groupBox = QGroupBox(self)
        self.groupBox.setTitle(self.label)
        self.groupBox.setStyleSheet("QGroupBox{border-radius: 15px; border: 2px solid gray; font-size: 18px; font-weight: bold;margin-top: 5ex;} QGroupBox::title{padding: -50 1 1 1;}")
        self.groupBoxLayout = QHBoxLayout(self.groupBox)

        ################################################################################################################
        ## The base list widgets, using these over M/View for speed of setup.
        self.allChecks_ListWidget = QListWidget(self)
        self.allChecks_ListWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.allChecks_ListWidget.itemEntered.connect(partial(self._disableMoveToBaseButtons))

        self.activeChecks_ListWidget = QListWidget(self)
        self.activeChecks_ListWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.activeChecks_ListWidget.itemEntered.connect(partial(self._disableMoveToActiveButtons))

        ################################################################################################################
        ## Button Layout
        self.buttonLayout = QVBoxLayout(self)
        self.moveToActiveButton = QPushButton(QIcon('{}\\iconmonstr-arrow-52-240PntRight.png'.format(CONST.ICONPATH)), '', self)
        self.moveToActiveButton.clicked.connect(partial(self._addToActiveList))
        self.moveToActiveButton.setToolTip('Add to active sanity checks for this dept')

        self.moveToBaseButton = QPushButton(QIcon('{}\\iconmonstr-arrow-52-240PntLeft.png'.format(CONST.ICONPATH)), '', self)
        self.moveToBaseButton.clicked.connect(partial(self._removeFromActiveList))
        self.moveToBaseButton.setToolTip('Remove from active sanity checks for this dept')
        self.moveToBaseButton.setEnabled(False)

        self.addAllToBaseButton = QPushButton(QIcon('{}\\iconmonstr-arrowPntLeft-32-240.png'.format(CONST.ICONPATH)), '', self)
        self.addAllToBaseButton.clicked.connect(partial(self._removeFromActiveList, False))
        self.addAllToBaseButton.setToolTip('Remove ALL from active sanity checks for this dept')
        self.addAllToBaseButton.setEnabled(False)

        self.addAllToActiveButton = QPushButton(QIcon('{}\\iconmonstr-arrowPntRight-32-240.png'.format(CONST.ICONPATH)), '', self)
        self.addAllToActiveButton.clicked.connect(partial(self._addToActiveList, False))
        self.addAllToActiveButton.setToolTip('Add ALL to active sanity checks for this dept')

        self.buttonLayout.addWidget(self.moveToActiveButton)
        self.buttonLayout.addWidget(self.moveToBaseButton)
        self.buttonLayout.addWidget(self.addAllToBaseButton)
        self.buttonLayout.addWidget(self.addAllToActiveButton)
        self.buttonLayout.addStretch(1)

        self.groupBoxLayout.addWidget(self.allChecks_ListWidget)
        self.groupBoxLayout.addLayout(self.buttonLayout)
        self.groupBoxLayout.addWidget(self.activeChecks_ListWidget)

        self.mainLayout.addWidget(self.groupBox)

    def _addData(self):
        self.allChecks_ListWidget.clear()
        self.activeChecks_ListWidget.clear()

        ## Add everything to the baseList that isn't in the activeList
        for eachItem in self.allChecks_List:
            if eachItem not in self.activeChecks_List:
                self.allChecks_ListWidget.addItem(eachItem)

        ## Now put the actives into the activeList
        for eachItem in self.activeChecks_List:
            self.activeChecks_ListWidget.addItem(eachItem)

    def _addToActiveList(self, selected = True):
        if selected:
            for eachItem in self.allChecks_ListWidget.selectedItems():
                name = eachItem.text()
                if name in self.allChecks_List:
                    self.allChecks_List.remove(name)

                if name not in self.activeChecks_List:
                    self.activeChecks_List.extend([name])
        else:
            count = self.allChecks_ListWidget.count()
            for x in range(count):
                name = self.allChecks_ListWidget.item(x).text()

                if name in self.allChecks_List:
                    self.allChecks_List.remove(name)

                if name not in self.activeChecks_List:
                    self.activeChecks_List.extend([name])
        self._addData()

    def _removeFromActiveList(self, selected = True):
        if selected:
            for eachItem in self.activeChecks_ListWidget.selectedItems():
                name = eachItem.text()
                if name in self.activeChecks_List:
                    self.activeChecks_List.remove(name)

                if name not in self.allChecks_List:
                    self.allChecks_List.extend([name])
        else:
            count = self.activeChecks_ListWidget.count()
            for x in range(count):
                name = self.activeChecks_ListWidget.item(x).text()

                if name in self.activeChecks_List:
                    self.activeChecks_List.remove(name)

                if name not in self.allChecks_List:
                    self.allChecks_List.extend([name])
        self._addData()

    def _disableMoveToBaseButtons(self, sender):
        self.moveToBaseButton.setEnabled(False)
        self.addAllToBaseButton.setEnabled(False)
        self.moveToActiveButton.setEnabled(True)
        self.addAllToActiveButton.setEnabled(True)
        self.activeChecks_ListWidget.setCurrentRow(-1)

    def _disableMoveToActiveButtons(self, sender):
        self.moveToActiveButton.setEnabled(False)
        self.addAllToActiveButton.setEnabled(False)
        self.moveToBaseButton.setEnabled(True)
        self.addAllToBaseButton.setEnabled(True)
        self.allChecks_ListWidget.setCurrentRow(-1)

class ConfigUI(QWidget):
    def __init__(self, parent = None, label = "Config"):
        QWidget.__init__(self, parent)
        self.label = label
        self.setWindowTitle(self.label)
        self.setObjectName(self.label)
        self.mainLayout = QVBoxLayout(self)
        self.config = loadConfig()
        self.uiDataStore = {}
        self.__initMainLayout()

    def __initMainLayout(self):
        """
        Setup the mainLayout for the UI
        :return:
        """
        self.checksLayout = QHBoxLayout(self)
        for checkDept, checkList in self.config["activechecks"].items():
            self.deptChecksList = ConfigCheckLists(self, checkDept, self.config['allChecks'], self.config["activechecks"][checkDept])
            self.checksLayout.addWidget(self.deptChecksList)
            self.uiDataStore[checkDept] = self.deptChecksList

        self.saveButton = QPushButton('Save')
        self.saveButton.clicked.connect(partial(self._saveConfig, checks = self.config["allChecks"]))

        self.cancelButton = QPushButton('Close')
        self.cancelButton.clicked.connect(partial(self.close))

        self.mainLayout.addLayout(self.checksLayout)
        self.mainLayout.addWidget(self.saveButton)
        self.mainLayout.addWidget(self.cancelButton)
        self.resize(1500, 500)

    def _saveConfig(self, checks = []):
        """
        For some reason the self.config['allChecks'] turns into an empty list here. So I am forcing a reload of this
        from the file before writing to it to preserve this list.
        :param checks:
        :return:
        """
        self.allChecks =  loadConfig()['allChecks']
        ## Process checks for which are on or off
        for checkDept, checkWidget in self.uiDataStore.items():
            validChecks = []
            count = checkWidget.activeChecks_ListWidget.count()
            for x in range(count):
                activeCheck = str(checkWidget.activeChecks_ListWidget.item(x).text())
                validChecks.append(activeCheck)

            self.config['activechecks'][checkDept] = validChecks

        ## Force the freaking allChecks to be correct!!!
        self.config['allChecks'] = self.allChecks

        ## Dump to yaml now
        _dumpYAML(self.config)
        print 'Config updated successfully.'
        self.close()


################### FUNCS
def loadConfig():
    configPath = os.path.realpath(__file__)
    configPath = configPath.split(os.path.sep)
    configPath = "\\".join(configPath[:-1])
    filePath = "%s\\CONFIG.yaml" % configPath
    data = _readYAML(filePath)
    data[1].close()
    return data[0]

def _readYAML(filePath):
    f = open(filePath, "r")
    data = yaml.load(f)
    return data, f

def _dumpYAML(data):
    configPath = os.path.realpath(__file__)
    configPath = configPath.split(os.path.sep)
    configPath = "\\".join(configPath[:-1])
    filePath = "%s\\CONFIG.yaml" % configPath
    with open(filePath, 'w') as outfile:
        outfile.write(yaml.dump(data))

# def widgets_at(pos):
#     """Return ALL widgets at `pos`
#     Arguments:
#         pos (QPoint): Position at which to get widgets
#     """
#     widgets = []
#     widget_at = qApp.widgetAt(pos)
#     while widget_at:
#         widgets.append(widget_at)
#         # Make widget invisible to further enquiries
#         widget_at.setAttribute(Qt.WA_TransparentForMouseEvents)
#         widget_at = qApp.widgetAt(pos)
#     # Restore attribute
#     for widget in widgets:
#         widget.setAttribute(Qt.WA_TransparentForMouseEvents, False)
#     return widgets