"""Controller Local/Global Switch - MAYA 2015

#====================================================
#
# DEVELOPMENT HISTORY
#               
#       
# TO DO
#               - In the long run setup little "L" and "G" shapes to attach to the local and Global Control. But for this, probably just use different colours and names, but the same Curve Shape
#
#
# RECENT FEATURES 
#               - Basic UI Setup
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
		# print "Horray we have a good selection"	
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


def nameSwitchRebuild(name,typeToReplace, replaceWith, nameEnd = "ctrl"):
    nameBits = name.split("_")
    print "nameBits :", nameBits
    newName = ""
    for i,bit in enumerate(nameBits):
        if bit == typeToReplace:
            newName = newName + replaceWith + "_"
        else:
            newName = newName + bit + "_"
      
    newName = newName + nameEnd
    return newName

def stripConstraintsFromGroup(ctrlGrp):
	"""Function to look at the children of the group and delete any constraints that are found in there"""
	constraintList = ["parentConstraint", "pointConstraint", "orientConstraint", "aimConstraint","scaleConstraint" ]
	children = cmds.listRelatives(ctrlGrp, children = True)
	for node in children:
		nType = cmds.nodeType(node)
		if len(nType.split("Constraint")) > 1: #If the node type string splits around the word "Constraint" then we have a constraint, so delete it.
			cmds.delete(node)


def ctrlRename(ctrlName, nameAddition):
	nameSplit = ctrlName.split("Ctrl")
	newName = ctrlName
	if len(nameSplit) > 1:
		newName = nameSplit[0] + nameAddition
	return newName

def shapeRecolour(obj, colourIndex):
	"""Function to loop through all shapes on a node and change: 2-dark grey, 13-red, 17-yellow, 18-cyan, 20-cream"""
	objShapes = cmds.listRelatives(obj, children = True, shapes =True)
	#Now loop through shape nodes and change their colour
	for shape in objShapes:
	    cmds.setAttr(shape + '.overrideEnabled', 1)
	    cmds.setAttr(shape + '.overrideColor', colourIndex)	# color Index to represent colour


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
		self.pmaSwitchNode = None

		self.ctrlsTw = QtGui.QTreeWidget()
		self.ctrlsTw.setToolTip("Please select the controller that you wish to create a local/Global Switch for and then click the button below.\nThis tool will only run on one control at a time")
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
			if len(mySel) == 1:
				for ctrl in mySel:
					treeItem = QtGui.QTreeWidgetItem(ctrl)
					treeItem.setText(0, ctrl)
					treeItem.setFlags(QtCore.Qt.ItemIsEnabled) #Set the Item so it cannot be selected
					self.ctrlsTw.addTopLevelItem(treeItem)
					self.ctrlList.append(ctrl)
			else:
				cmds.warning("Incorrect Controller Selection, please only select a single controller")


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

	def checkSwitchCtrlAtt(self):
		self.switchCtrlAtt = None
		if self.switchCtrlTw.currentItem():
			self.switchCtrlAtt = self.switchCtrlTw.currentItem().text(0)

	def switchBuild(self):
		"""Method to loop through controls in the self.ctrlList, duplicate them and their groups and then create a Global/Local Switch"""
		cmds.undoInfo(openChunk=True)		
		self.checkSwitchCtrlAtt()	
		#Setup plusMinusAverage Reversing Node
		pMAName = nameSwitchRebuild(self.switchCtrl, "cv", "pma", nameEnd = self.switchCtrlAtt + "Switch")
		myRigPm = cmds.shadingNode('plusMinusAverage', asUtility=True, name= pMAName)
		self.pmaSwitchNode = myRigPm
		cmds.setAttr(self.pmaSwitchNode + ".operation", 2)
		cmds.setAttr(self.pmaSwitchNode + ".input1D[0]", 1)
		# print "MasterStuff :",self.masterCtrl,self.masterCtrlAtt
		cmds.connectAttr(self.switchCtrl + "." + self.switchCtrlAtt, self.pmaSwitchNode + ".input1D[1]")

		#Now we need to duplicate the control twice. Rename the orginal to a "Ghost Control" and label up the others as local and global Controls, first of all find the Control Group
		currentCtrlGroup = cmds.listRelatives(self.ctrlList[0], parent = True)
		newGlobalCtrlPack = (cmds.duplicate(currentCtrlGroup, renameChildren=True))
		stripConstraintsFromGroup(newGlobalCtrlPack)  #Delete out any constraint Nodes in there
		newGlobalGrpName = ctrlRename(newGlobalCtrlPack[0], "GlobalCtrl")
		newGlobalCtrlName = ctrlRename(newGlobalCtrlPack[1], "GlobalCtrl")
		cmds.rename(newGlobalCtrlPack[0], newGlobalGrpName)
		cmds.rename(newGlobalCtrlPack[1], newGlobalCtrlName)
		shapeRecolour(newGlobalCtrlName, 13) # Colour Global Control Red

		newLocalCtrlPack = cmds.duplicate(currentCtrlGroup, renameChildren=True)
		stripConstraintsFromGroup(newLocalCtrlPack)  #Delete out any constraint Nodes in there
		newLocalGrpName = ctrlRename(newLocalCtrlPack[0], "LocalCtrl")
		newLocalCtrlName = ctrlRename(newLocalCtrlPack[1], "LocalCtrl")
		cmds.rename(newLocalCtrlPack[0], newLocalGrpName)
		cmds.rename(newLocalCtrlPack[1], newLocalCtrlName)
		shapeRecolour(newLocalCtrlName, 17) # Colour Local Control Yellow

		#Rename the original Controls to be Ghosts
		currentGroupGhostName = ctrlRename(currentCtrlGroup[0], "Ghost")
		currentCtrlGhostName = ctrlRename(self.ctrlList[0], "Ghost")
		cmds.rename(currentCtrlGroup, currentGroupGhostName)
		cmds.rename(self.ctrlList[0], currentCtrlGhostName)
		shapeRecolour(currentCtrlGhostName, 2) #2 is dark grey

		#Now connect up the visibility of the new controls
		cmds.connectAttr(self.pmaSwitchNode + ".output1D", newLocalCtrlName + ".visibility")
		cmds.connectAttr(self.switchCtrl + "." + self.switchCtrlAtt, newGlobalCtrlName + ".visibility")


if __name__ == "__main__":
	TDFR_ControllerGlobalLocalSwitch_Ui()
