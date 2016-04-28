"""Controller Local/Global Switch - MAYA 2015

#====================================================
#
# DEVELOPMENT HISTORY
#               
#       
# TO DO
#               - 
#
#
# RECENT FEATURES 
#               - 
#====================================================
# GUIDE
#               - 
#
#
# IMPORTANT NOTES
#               - 
#
###########################################################################################################################################################
"""

__author__ = "3DFramework"
__version__ = "1.0"


from PySide import QtCore, QtGui
import maya.cmds as cmds


#====================================================
#   Create IK Setup UI
#====================================================
class TDFR_ControllerGlobalLocalSwitch_Ui(MayaQWidgetDockableMixin, QtGui.QDialog):
	"""Class to block out all the main functionality of the IKSetup UI"""
	def __init__(self):
		super(TDFR_ControllerGlobalLocalSwitch_Ui, self).__init__()
		self.ctrlTw = QtGui.QTreeWidget()
		self.ctrlTw.setToolTip("Please select the controller that you wish to create a local/Global Switch for and then click the button below")
		self.ctrlTw.setHeaderLabel("")
		self.ctrlLbl = QtGui.QLabel("Specify Controller to add switch to")
		self.ctrlBtn = QtGui.QPushButton("Add Selected Control", self)
		# self.ctrlBtn.clicked.connect(self.ctrlBtnPress)
		self.ctrlClearBtn = QtGui.QPushButton("Clear", self)
		self.ctrlClearBtn.setMaximumWidth(40)
		# self.ctrlClearBtn.clicked.connect(self.clearctrls)

		self.switchCtrlTw = QtGui.QTreeWidget()
		self.switchCtrlTw.setToolTip("Please select the switch Control that will control the switch system, and then highlight the attribute that you want to use to control the switch")
		self.switchCtrlTw.setHeaderLabel("")
		self.switchCtrlLbl = QtGui.QLabel("Please choose the switch Control Switch Attribute")
		self.switchCtrlBtn = QtGui.QPushButton("Add Selected switch Control", self)	
		# self.switchCtrlBtn.clicked.connect(self.switchCtrlBtnPress)
		self.switchCtrlClearBtn = QtGui.QPushButton("Clear", self)
		self.switchCtrlClearBtn.setMaximumWidth(40)
		# self.switchCtrlClearBtn.clicked.connect(self.clearswitchCtrl)

		masterSwitchFrame = QtGui.QFrame(self) # Create frame and Layout to hold all the User List View
		masterSwitchFrame.setFrameShape(QtGui.QFrame.StyledPanel)

		uiTopHLayout = QtGui.QHBoxLayout()

		ctrlLayout = QtGui.QVBoxLayout()
		ctrlButtonLayout = QtGui.QHBoxLayout()
		ctrlButtonLayout.addWidget(self.ctrlBtn)
		ctrlButtonLayout.addWidget(self.ctrlClearBtn)
		ctrlLayout.addWidget(self.ctrlLbl)
		ctrlLayout.addWidget(self.ctrlTw)
		ctrlLayout.addLayout(ctrlButtonLayout)

		switchLayout = QtGui.QVBoxLayout()
		switchButtonLayout = QtGui.QHBoxLayout()
		switchButtonLayout.addWidget(self.switchCtrlBtn)
		switchButtonLayout.addWidget(self.switchCtrlClearBtn)
		switchLayout.addWidget(self.switchCtrlLbl)
		switchLayout.addWidget(self.switchCtrlTw)
		switchLayout.addLayout(switchButtonLayout)

		uiTopHLayout.addLayout(ctrlLayout)
		uiTopHLayout.addLayout(switchLayout)

		uiTotalLayout = QtGui.QVBoxLayout(masterSwitchFrame)
		uiTotalLayout.addLayout(uiTopHLayout)

		self.executeSwitchBtn = QtGui.QPushButton('Build the FK to IK System')
		# self.executeSwitchBtn.clicked.connect(self.switchBuild)
		self.executeSwitchBtn.setToolTip("Please hit the big green button when all the rest of the options are filled out, and it will hopefully build you an FK to IK switch system.")
		self.executeSwitchBtn.setMinimumHeight(80)
		self.executeSwitchBtn.setMinimumWidth(470)
		self.executeSwitchBtn.setStyleSheet("background-color: green")
		uiTotalLayout.addWidget(self.executeSwitchBtn)

		self.setGeometry(300, 300, 550, 360)
		self.setWindowTitle('Control Global to Local Switch')    
		self.show()


if __name__ == "__main__":
	TDFR_ControllerGlobalLocalSwitch_Ui()
