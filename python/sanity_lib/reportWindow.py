'''
Created on 20/09/2012
@author: jamesd
'''
import logging
from functools import partial
from PySide.QtCore import *
from PySide.QtGui import *

try:
    import maya.cmds as cmds
    import python.sanity_lib.CONST as CONST
except ImportError:pass
logger = logging.getLogger(__name__)

ICONPATH = CONST.ICONPATH

SEP = " |  | " ## Used in the listWidgets to make it easier to read the long names
class ReportWindow(QWidget):
    def __init__(self, parent = None, label =  {}):
        ## Window for use in maya reporting
        QWidget.__init__(self, parent)
        self.parent = parent
        self.label = label
        self.setWindowTitle(self.label)
        self.setObjectName(self.label)
        self.mainLayout = QVBoxLayout(self)
        self.data = []
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

        self.filterLayout = QHBoxLayout(self)
        self.filterLabel = QLabel('Filter', self)
        self.filter = QLineEdit(self)
        self.filter.textChanged.connect(self._applyFilter)
        self.filterLayout.addWidget(self.filterLabel)
        self.filterLayout.addWidget(self.filter)

        self.groupBoxLayout.addWidget(self.reportTree)
        self.groupBoxLayout.addLayout(self.filterLayout)
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
        ## DEFAULT Right click menu actions
        self.deleteAction = QAction('Delete', self)
        self.deleteAction.setIcon(QIcon("{}/iconmonstr-trash-can-5-240.png".format(CONST.ICONPATH)))
        self.deleteAction.triggered.connect(partial(self.processItems, case = 'delete'))

        ## Add the defaults now
        self.rightClickMenu.addAction(self.deleteAction)

    def addData(self, data = []):
        """
        Process the data into the report window
        :param data: list of items to add to the listWidget
        :type data: list
        :return:
        """
        self.reportTree.clear()
        self.data = []
        stash = data
        for eachD in data:
            if eachD:
                ## Add the item with a cleaner more readable spacer than maya's default |
                self.reportTree.addItem(eachD.replace("|", SEP))
                self.data.extend([eachD])
                ## Now check to see if there are any more to report with the same name such as duplicate items
                ## Basically easier to read in the treeView
                for eachStsh in stash:
                    if eachStsh:
                        if eachStsh != eachD:
                            if eachStsh.split("|")[-1] == eachD.split("|")[-1]:
                                self.reportTree.addItem(eachStsh.replace("|", SEP))
                                self.data.extend([eachStsh])
                                data.remove(eachStsh)
            ## Now add a little sep between em
            self.reportTree.addItem("-----")

    def processItems(self, sender = None, all = False, case = ''):
        cmds.undoInfo(openChunk = True)
        cmds.select(clear = True)
        if not all:
            for eachItem in self._getSelItems():
                itemName = eachItem.text().replace(SEP, "|")
                if not cmds.objExists(itemName):
                    itemName = itemName.split("|")[-1] or None

                if itemName:
                    if case == 'select':
                        cmds.select(itemName, add = True, ne = True)
                    elif case == 'delete':
                        cmds.delete(itemName)
                    elif case == 'deleteCH':
                        cmds.delete(itemName, ch = True)
        else:
            count = self.reportTree.count()
            items = []
            for x in range(count):
                if "-----" not in self.reportTree.item(x).text():
                    itemName = self.reportTree.item(x).text().replace(SEP, "|")
                    if not cmds.objExists(itemName):
                        itemName = itemName.split("|")[-1] or None
                    if itemName:
                        items.extend([itemName])

            if case == 'select':
                cmds.select(items, r = True, ne = True)
            elif case == 'delete':
                cmds.delete(items)
            elif case == 'deleteCH':
                cmds.delete(items, ch = True)

        cmds.undoInfo(closeChunk = True)

    def _getSelItems(self):
        items = [item for item in self.reportTree.selectedItems() if item.text() != '-----']
        return items

    def _applyFilter(self):
        self.reportTree.clear()
        filterText = self.filter.text()
        for eachItem in self.data:
            if filterText in eachItem.split("|")[-1]:
                self.reportTree.addItem(eachItem.replace("|", SEP))
        self.reportTree.addItem("-----")

    def showRightClickMenu(self, position):
        self.rightClickMenu.exec_(self.reportTree.viewport().mapToGlobal(position))
        self.rightClickMenu.show()
