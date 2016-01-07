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

class SanityUI(QMainWindow):
    def __init__(self, parent = None):
        QMainWindow.__init__(self, parent)
        self.setWindowTitle('Sanity Check')
        self.setObjectName('Sanity Check')
        self.mainLayout = QVBoxLayout(self)
        self.state = 'rig'
        self.checkBoxes = []
        self._initCheckDock()
        self._initCheckBoxes()
        self._initChecksPassed()
        self.tabWidget = QTabWidget(self)
        self.setCentralWidget(self.tabWidget)
        self.addToolBar(self._initToolBar())
        self.mainLayout.addStretch(1)

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
        self.dock.setWindowTitle('Peform Sanity Checks:')
        self.dockWidget = QWidget()
        self.dock.setWidget(self.dockWidget)
        self.dockLayout = QVBoxLayout(self.dockWidget)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock)

    def _initChecksPassed(self):
        self.dockStatus = QDockWidget(self)
        self.dockStatus.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.dockStatus.setWindowTitle('Status:')
        self.docStatuskWidget = QWidget()
        self.dockStatus.setWidget(self.docStatuskWidget)
        self.dockStatusLayout = QHBoxLayout(self.docStatuskWidget)

        self.failedList = QListWidget(self)
        self.failedList.setEnabled(False)
        self.passedList = QListWidget(self)
        self.passedList.setEnabled(False)

        self.dockStatusLayout.addWidget(self.failedList)
        self.dockStatusLayout.addWidget(self.passedList)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dockStatus)

    def _initCheckBoxes(self, stateCB = None):
        myPath = os.path.realpath(__file__)
        myPath = myPath.split(os.path.sep)
        myPath = "\\".join(myPath[:-1])
        filePath = "%s\\lib\\CONFIG.yaml" % myPath
        self.checkLayout = QVBoxLayout(self)

        if self.checkBoxes:
            for eachCBox in self.checkBoxes:
                eachCBox.close()
                eachCBox = None

        if hasattr(self, 'performChecks'):
            self.performChecks.close()
        self.checkBoxes = []
        self.config = self._readYAML(filePath)
        if stateCB:
            self.state = stateCB

        self.checkList = self.config['checks'][self.state]
        for eachCheck in self.checkList:
            self.radioButton = QRadioButton(eachCheck, self)
            self.radioButton.setObjectName(eachCheck)
            self.radioButton.setAutoExclusive(False)
            self.radioButton.setChecked(True)
            self.checkBoxes.extend([self.radioButton])
            self.checkLayout.addWidget(self.radioButton)

        self.dockLayout.addLayout(self.checkLayout)

    def _performChecks(self):
        data = sanity.sanityCheck()
        for eachRB in self.checkBoxes:
            if eachRB.objectName() in data.keys():
                self.tab = QWidget(self)
                self.reportLayout = QVBoxLayout(self)
                self.reportQL = ReportWindow(self, eachRB.objectName())
                self.reportQL.addData(data[eachRB.objectName()])

    def _readYAML(self, filePath):
        f = open(filePath, "r")
        data = yaml.load(f)
        return data



class ReportWindow(QWidget):
    def __init__(self, parent = None, label = {}):
        QWidget.__init__(self, parent)
        self.setWindowTitle('Reporter')
        self.setObjectName('Reporter')

        self.data = {}
        self.label = label

        self.__initMainLayout()

    def __initMainLayout(self):
        """
        Setup the mainLayout for the reporter window
        :return:
        """
        self.mainLayout = QVBoxLayout(self)

        self.groupBox = QGroupBox(self)
        self.groupBox.setTitle('{} report'.format(self.label))
        self.groupBox.setStyleSheet("QGroupBox{border: 1px solid gray; border-radius: 9px;} QGroupBox::title {subcontrol-origin: margin;left: 100px;padding: -5 3px 0 3px;}")
        self.groupBoxLayout = QVBoxLayout(self.groupBox)

        self.reportTree = QListWidget(self)

        self.groupBoxLayout.addWidget(self.reportTree)
        self.mainLayout.addWidget(self.groupBox)

    def addData(self, dataList = []):
        """
        Process the data into the report window
        :param data: list of items to add to the listWidget
        :type data: list
        :return:
        """
        self.reportTree.clear()
        for eachItem in dataList:
            self.reportTree.addItem(eachItem)









def main():
    app = QApplication(sys.argv)
    #w = ReportWindow(label = "test")
    w = SanityUI()
    w.show()

    #w.addData(['test', 'test1', 'test2'])
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()