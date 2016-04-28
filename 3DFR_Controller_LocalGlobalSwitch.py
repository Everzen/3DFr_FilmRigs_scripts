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
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin


def ctrlSelectionFilter():
	validSelection = False
	mySel = cmds.ls(sl=True)
	myJnts = cmds.ls(mySel, type = "joint") #Filter through the selection in order make sure all things are joints.
	if len(myJnts) == 0 and len(mySel) > 0: #This means we have at least 1 none joint selected
		print "Horray we have a good selection"	
		validSelection = True
	else: #We have 2 joints so we can continue - Now work down from parent to find the child
		cmds.warning('Incorrect Initial Selection - Please select just your controls (no joints)')#If we do not have 2 joints selected then exit
	return validSelection


def checkRepeatSelection(selList, checkSwitchJointList, checkMessage, isJoint=True):
	"""Function to check if a selection is repeated between too lists. This deal with joints which we do not need to this tool"""
	validSelection = True
	checkList = checkSwitchJointList
	if isJoint: checkList = [sJ.getName() for sJ in checkSwitchJointList] #Colect Names since we have switch Joints, we need names to comapre to the selection
	intersectionSet = set(selList).intersection(set(checkList)) #Form a set from the intersection of these lists, if Items are in the set, then then they are repeated! 
	if len(intersectionSet) > 0:
		validSelection = False
		cmds.warning('Incorrect Initial Selection - You have selected some items that match those in the ' + checkMessage + " List")#If we do not have 2 joints selected then exit
	return validSelection


#====================================================
#   Create IK Setup UI
#====================================================
class TDFR_ControllerGlobalLocalSwitch_Ui(MayaQWidgetDockableMixin, QtGui.QDialog):
	"""Class to block out all the main functionality of the IKSetup UI"""
	def __init__(self):
		super(TDFR_ControllerGlobalLocalSwitch_Ui, self).__init__()
		self.ctrlList = []
		self.switchCtrl = None
		self.switchCtrlAtts = []
		self.switchCtrlAtt = None


		self.ctrlsTw = QtGui.QTreeWidget()
		self.ctrlsTw.setToolTip("Please select the controller that you wish to create a local/Global Switch for and then click the button below")
		self.ctrlsTw.setHeaderLabel("")
		self.ctrlsLbl = QtGui.QLabel("Specify Controller to add switch to")
		self.ctrlsBtn = QtGui.QPushButton("Add Selected Control", self)
		self.ctrlsBtn.clicked.connect(self.ctrlBtnPress)
		self.ctrlsClearBtn = QtGui.QPushButton("Clear", self)
		self.ctrlsClearBtn.setMaximumWidth(40)
		self.ctrlsClearBtn.clicked.connect(self.clearCtrls)

		self.switchCtrlTw = QtGui.QTreeWidget()
		self.switchCtrlTw.setToolTip("Please select the switch Control that will control the switch system, and then highlight the attribute that you want to use to control the switch")
		self.switchCtrlTw.setHeaderLabel("")
		self.switchCtrlLbl = QtGui.QLabel("Please choose the switch Control Switch Attribute")
		self.switchCtrlBtn = QtGui.QPushButton("Add Selected switch Control", self)	
		self.switchCtrlBtn.clicked.connect(self.switchCtrlBtnPress)
		self.switchCtrlClearBtn = QtGui.QPushButton("Clear", self)
		self.switchCtrlClearBtn.setMaximumWidth(40)
		self.switchCtrlClearBtn.clicked.connect(self.clearSwitchCtrl)

		masterSwitchFrame = QtGui.QFrame(self) # Create frame and Layout to hold all the User List View
		masterSwitchFrame.setFrameShape(QtGui.QFrame.StyledPanel)

		uiTopHLayout = QtGui.QHBoxLayout()

		ctrlLayout = QtGui.QVBoxLayout()
		ctrlButtonLayout = QtGui.QHBoxLayout()
		ctrlButtonLayout.addWidget(self.ctrlsBtn)
		ctrlButtonLayout.addWidget(self.ctrlsClearBtn)
		ctrlLayout.addWidget(self.ctrlsLbl)
		ctrlLayout.addWidget(self.ctrlsTw)
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

		self.executeSwitchBtn = QtGui.QPushButton('Build Global/Local Switch for the Control/s')
		self.executeSwitchBtn.clicked.connect(self.switchBuild)
		self.executeSwitchBtn.setToolTip("Please hit the big green button when all the rest of the options are filled out, and it will hopefully build you a Global/Local switch system\nfor each of the controls in the control list.")
		self.executeSwitchBtn.setMinimumHeight(80)
		self.executeSwitchBtn.setMinimumWidth(470)
		self.executeSwitchBtn.setStyleSheet("background-color: green")
		uiTotalLayout.addWidget(self.executeSwitchBtn)

		self.setGeometry(300, 300, 550, 360)
		self.setWindowTitle('Control Global to Local Switch')    
		self.show()


	def ctrlBtnPress(self):
		"""Function to filter through the selection, make sure that we do not have any joints and add the remaining items to the Ctrls List"""
		self.clearCtrls()
		mySel = cmds.ls(sl=True)
		if ctrlSelectionFilter() and self.checkAllSelections(mySel):
			mySel = cmds.ls(sl=True)
			for ctrl in mySel:
				treeItem = QtGui.QTreeWidgetItem(ctrl)
				treeItem.setText(0, ctrl)
				treeItem.setFlags(QtCore.Qt.ItemIsEnabled) #Set the Item so it cannot be selected
				self.ctrlsTw.addTopLevelItem(treeItem)
				self.ctrlList.append(ctrl)


	def switchCtrlBtnPress(self):
		"""Function to filter through the selection, make sure that we do not have any joints and add the remaining items to the Ctrls List"""
		self.clearSwitchCtrl()
		mySel = cmds.ls(sl=True)
		if ctrlSelectionFilter() and self.checkAllSelections(mySel):
			if len(mySel) == 1:
				self.switchCtrl = mySel[0]
				masterAtts = cmds.listAttr(mySel[0], s=True, r=True, w=True, c=True, userDefined=True) #This will give a list of readable, keyable, scalar, user defined attributes
				for att in masterAtts:
					treeItem = QtGui.QTreeWidgetItem(att)
					treeItem.setText(0, att)
					self.switchCtrlTw.addTopLevelItem(treeItem)
					self.switchCtrlAtts.append(att)
			else: cmds.warning("Please select a single node that has user defined attributes added, to act as the Master Control")


	def checkAllSelections(self,mySel):
		validSelection = True
		if not checkRepeatSelection(mySel, self.ctrlList, "Controls", isJoint=False) : validSelection = False
		if not checkRepeatSelection(mySel, [self.switchCtrl], "Switch Control", isJoint=False) : validSelection = False
		return validSelection

	def clearCtrls(self):
		self.ctrlsTw.clear()
		self.ctrlList = []

	def clearSwitchCtrl(self):
		self.switchCtrlTw.clear()
		self.switchCtrl = None
		self.switchCtrlAtts = []
		self.switchCtrlAtt = None

	def switchBuild(self):
		"""Method to loop through controls in the self.ctrlList, duplicate them and their groups and then create a Global/Local Switch"""
		pass


if __name__ == "__main__":
	TDFR_ControllerGlobalLocalSwitch_Ui()
