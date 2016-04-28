"""FK TO IK SWITCH TOOL - MAYA 2015

#====================================================
#
# DEVELOPMENT HISTORY
#				- Some tool Tips added.
#		
# TO DO
#				- Complete Tool Tips
#				- Record Help Video of tool Set
#				- Undo Queue save is added, but is not working - Maybe try and fix, but for now save before execution of tool
#
#====================================================
# GUIDE
#				- Use Tool Tips for now, but add this guide
#
# IMPORTANT NOTES
#               - This setup does not deal with frozen transforms on objects. Make sure that all controls especially have not had transforms frozen
#
###########################################################################################################################################################
"""
__author__ = "3DFramework"
__version__ = "1.0"


from PySide import QtGui, QtCore
import maya.OpenMayaUI as apiUI
from shiboken import wrapInstance

import maya.cmds as cmds

#############################################################################################################


#############################################################################################################

def getMayaWindow():
	"""
	Get the main Maya window as a QtGui.QMainWindow instance
	@return: QtGui.QMainWindow instance of the top level Maya windows
	"""
	ptr = apiUI.MQtUtil.mainWindow()
	if ptr is not None:
		return wrapInstance(long(ptr), QtGui.QWidget)


#####################################################################FUNCTION CODE#############################
def jointSelectionFilter():
	validSelection = False
	mySel = cmds.ls(sl=True)
	myJnts = cmds.ls(mySel, type = "joint") #Filter through the selection in order make sure all things are joints.
	if len(myJnts) == 2 and len(mySel) == 2:
		print "Horray we have a good selection"	
		validSelection = True
	else: #We have 2 joints so we can continue - Now work down from parent to find the child
		cmds.warning('Incorrect Initial Selection - Please select just 1 start joint and 1 end joint')#If we do not have 2 joints selected then exit
	return validSelection

#jointSelectionFilter()

def checkRepeatSelection(selList, checkSwitchJointList, checkMessage, isJoint=True):
	validSelection = True
	checkList = checkSwitchJointList
	if isJoint: checkList = [sJ.getName() for sJ in checkSwitchJointList] #Colect Names since we have switch Joints, we need names to comapre to the selection
	selCount = len(selList) #Check selection count
	#print "SelCount = " + str(selCount)
	#print "CheckList Count " + str(len(checkSwitchJointList))
	#checkCount = len(list(set(selList) - set(checkSwitchJointList))) #check the length of the list formed by checking for set duplicates
	#print "Sel  ", set(selList)
	#print "Check ", set(checkSwitchJointList)
	intersectionSet = set(selList).intersection(set(checkList)) #Form a set from the intersection of these lists, if Items are in the set, then then they are repeated! 
	#print "Intersection Set : " + str(intersectionSet)
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

def nameConstraintRebuild(name,searchString,typeToReplace, replaceWith, nameEnd = "ctrl"):
    nameBits = name.split("_")
       
    newName = ""
    for i,bit in enumerate(nameBits):
        newSplit = bit.split(searchString)
        if len(newSplit) != 1:
                #print "Gotta : " + str(i)
                for j,nameEle in enumerate(nameBits):
                    if nameEle == typeToReplace:
                        newName = newName + replaceWith + "_"
                    elif  j==i:
                        newName = newName + searchString + newSplit[1] + "_"
                    else:
                        newName = newName + nameEle + "_"
                  
    newName = newName + nameEnd
    return newName


class SwitchJoint(object):
	def __init__(self,jntName):
		self.name = jntName
		self.jntTreeItem = QtGui.QTreeWidgetItem()
		self.jntTreeItem.setFlags(QtCore.Qt.ItemIsEnabled) #Set the Item so it cannot be selected
		self.jntTreeItem.setText(0, jntName)

	def getName(self):
		return self.name

	def getTreeItem(self):
		return self.jntTreeItem



class JointHierarchy():
	def __init__(self,startJoint, endJoint):
		self.startJoint = SwitchJoint(startJoint)
		self.endJoint = SwitchJoint(endJoint)
		self.jointList = [self.endJoint]
		self.findParentJoint(self.endJoint)
		self.jointList = list(reversed(self.jointList))
		# print "My joint list : " 
		# for jnt in self.jointList: 
		# 	print jnt.getName()


	def findParentJoint(self, jnt):
		parentJoint = None
		myParent = cmds.listRelatives(jnt.getName(), allParents=True)
		myJointParent = cmds.ls(myParent, type = 'joint')
		if len(myJointParent) == 1: #We have a single joint parent
			newSwitchJoint = SwitchJoint(myJointParent[0])
			self.jointList.append(newSwitchJoint)
			if myJointParent[0] != self.startJoint.getName():
				self.findParentJoint(newSwitchJoint)

	def getJoints(self):
		return self.jointList


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

#####################################################################WIDGET CODE#############################
class JointTw(QtGui.QTreeWidget):
	def __init__(self, parent=getMayaWindow()):
		super(JointTw, self).__init__()
		self.setHeaderLabel("")
		self.jointList = []

	def getJoints(self):
		return self.jointList

	def setJoints(self, jntList):
		self.jointList = jntList
		self.populate()

	def populate(self):
		self.clear()
		for i, jnt in enumerate(self.jointList):
			if i == 0:
				self.addTopLevelItem(jnt.getTreeItem())
				jnt.getTreeItem().setExpanded(True)
			else:
				parentTreeItem = self.jointList[i-1].getTreeItem()
				parentTreeItem.addChild(jnt.getTreeItem())
				jnt.getTreeItem().setExpanded(True)







##MAIN FUNCTIONALITY######################################################
class FRFKtoIKSwitchUI(QtGui.QWidget):
	def __init__(self, parent=getMayaWindow()):
		super(FRFKtoIKSwitchUI, self).__init__(None, QtCore.Qt.WindowStaysOnTopHint) #This keeps the Window on Top
		
		self.fkJointList = [] #Create lists to be filled with SwitchJoints for the tool
		self.ikJointList = []
		self.masterJointList = []

		self.fkCtrlList = []
		self.ikCtrlList = []

		self.masterCtrl = None
		self.masterCtrlAtts = []
		self.masterCtrlAtt = None
		self.pmaSwitchNode = None

		self.fkJointTw = JointTw()
		self.fkJointTw.setToolTip("Please select the beginning and end FK Joints, and then click the button below")
		self.fkJointLbl = QtGui.QLabel("Specify FK Joints")
		self.fkJointBtn = QtGui.QPushButton("Add Selected FK Joints", self)
		self.fkJointBtn.clicked.connect(self.fkJointBtnPress)
		self.fkJointClearBtn = QtGui.QPushButton("Clear", self)
		self.fkJointClearBtn.setMaximumWidth(40)
		self.fkJointClearBtn.clicked.connect(self.clearFkJoints)

		self.fkCtrlsTw = QtGui.QTreeWidget()
		self.fkCtrlsTw.setToolTip("Please select the FK controls for the FK joints and then click the button below")
		self.fkCtrlsTw.setHeaderLabel("")
		self.fkCtrlsLbl = QtGui.QLabel("Specify FK Controls")
		self.fkCtrlsBtn = QtGui.QPushButton("Add Selected FK Controls", self)
 		self.fkCtrlsBtn.clicked.connect(self.fkCtrlBtnPress)
		self.fkCtrlsClearBtn = QtGui.QPushButton("Clear", self)
		self.fkCtrlsClearBtn.setMaximumWidth(40)
		self.fkCtrlsClearBtn.clicked.connect(self.clearFkCtrls)

		self.ikJointTw = JointTw()
		self.ikJointTw.setToolTip("Please select the beginning and end IK Joints, and then click the button below")
		self.ikJointLbl = QtGui.QLabel("Specify IK Joints")
		self.ikJointBtn = QtGui.QPushButton("Add Selected IK Joints", self)
		self.ikJointBtn.clicked.connect(self.ikJointBtnPress)
		self.ikJointClearBtn = QtGui.QPushButton("Clear", self)
		self.ikJointClearBtn.setMaximumWidth(40)
		self.ikJointClearBtn.clicked.connect(self.clearIkJoints)

		self.ikCtrlsTw = QtGui.QTreeWidget()
		self.ikCtrlsTw.setToolTip("Please select the IK controls for the IK joints and then click the button below")
		self.ikCtrlsTw.setHeaderLabel("")
		self.ikCtrlsLbl = QtGui.QLabel("Specify IK Controls")
		self.ikCtrlsBtn = QtGui.QPushButton("Add Selected IK Controls", self)
		self.ikCtrlsBtn.clicked.connect(self.ikCtrlBtnPress)
		self.ikCtrlsClearBtn = QtGui.QPushButton("Clear", self)
		self.ikCtrlsClearBtn.setMaximumWidth(40)
		self.ikCtrlsClearBtn.clicked.connect(self.clearIkCtrls)

		self.masterJointTw = JointTw()
		self.masterJointTw.setToolTip("Please select the beginning and end Master/Skin Joints, and then click the button below")
		self.masterJointLbl = QtGui.QLabel("Specify Master/Skin Rig Joints")
		self.masterJointBtn = QtGui.QPushButton("Add Selected Master/Skin Joints", self)
		self.masterJointBtn.clicked.connect(self.masterJointBtnPress)
		self.masterJointClearBtn = QtGui.QPushButton("Clear", self)
		self.masterJointClearBtn.setMaximumWidth(40)
		self.masterJointClearBtn.clicked.connect(self.clearMasterJoints)

		self.masterCtrlTw = QtGui.QTreeWidget()
		self.masterCtrlTw.setToolTip("Please select the Master Control that will control the switch system, and then highlight the attribute that you want to use to control the switch")
		self.masterCtrlTw.setHeaderLabel("")
		self.masterCtrlLbl = QtGui.QLabel("Please choose the Master Control Switch Attribute")
		self.masterCtrlBtn = QtGui.QPushButton("Add Selected Master Control", self)	
		self.masterCtrlBtn.clicked.connect(self.masterCtrlBtnPress)
		self.masterCtrlClearBtn = QtGui.QPushButton("Clear", self)
		self.masterCtrlClearBtn.setMaximumWidth(40)
		self.masterCtrlClearBtn.clicked.connect(self.clearMasterCtrl)

		masterJointFrame = QtGui.QFrame(self) # Create frame and Layout to hold all the User List View
		masterJointFrame.setFrameShape(QtGui.QFrame.StyledPanel)
		topUIVLayout = QtGui.QVBoxLayout(masterJointFrame)

		rigHLayout = QtGui.QHBoxLayout()

		fkLayout = QtGui.QVBoxLayout()
		fkLayout.addWidget(self.fkJointLbl)
		fkLayout.addWidget(self.fkJointTw)
		fkJointButtonLayout = QtGui.QHBoxLayout()
		fkJointButtonLayout.addWidget(self.fkJointBtn)
		fkJointButtonLayout.addWidget(self.fkJointClearBtn)
		fkLayout.addLayout(fkJointButtonLayout)
		fkLayout.addWidget(self.fkCtrlsLbl)
		fkLayout.addWidget(self.fkCtrlsTw)
		fkCtrlsButtonLayout = QtGui.QHBoxLayout()
		fkCtrlsButtonLayout.addWidget(self.fkCtrlsBtn)
		fkCtrlsButtonLayout.addWidget(self.fkCtrlsClearBtn)
		fkLayout.addLayout(fkCtrlsButtonLayout)

		ikLayout = QtGui.QVBoxLayout()
		ikLayout.addWidget(self.ikJointLbl)
		ikLayout.addWidget(self.ikJointTw)
		ikJointButtonLayout = QtGui.QHBoxLayout()
		ikJointButtonLayout.addWidget(self.ikJointBtn)
		ikJointButtonLayout.addWidget(self.ikJointClearBtn)
		ikLayout.addLayout(ikJointButtonLayout)		
		ikLayout.addWidget(self.ikCtrlsLbl)
		ikLayout.addWidget(self.ikCtrlsTw)
		ikCtrlButtonLayout = QtGui.QHBoxLayout()
		ikCtrlButtonLayout.addWidget(self.ikCtrlsBtn)
		ikCtrlButtonLayout.addWidget(self.ikCtrlsClearBtn)
		ikLayout.addLayout(ikCtrlButtonLayout)		

		masterRigLayout = QtGui.QVBoxLayout()
		masterRigLayout.addWidget(self.masterJointLbl)
		masterRigLayout.addWidget(self.masterJointTw)
		masterJointButtonLayout = QtGui.QHBoxLayout()
		masterJointButtonLayout.addWidget(self.masterJointBtn)
		masterJointButtonLayout.addWidget(self.masterJointClearBtn)	
		masterRigLayout.addLayout(masterJointButtonLayout)		
		masterRigLayout.addWidget(self.masterCtrlLbl)
		masterRigLayout.addWidget(self.masterCtrlTw)
		masterCtrlButtonLayout = QtGui.QHBoxLayout()
		masterCtrlButtonLayout.addWidget(self.masterCtrlBtn)
		masterCtrlButtonLayout.addWidget(self.masterCtrlClearBtn)		
		masterRigLayout.addLayout(masterCtrlButtonLayout)		

		rigHLayout.addLayout(fkLayout)
		rigHLayout.addLayout(ikLayout)
		rigHLayout.addLayout(masterRigLayout)

		nameStringLayout = QtGui.QVBoxLayout()
		nameStringLbl = QtGui.QLabel("Please name descriptor:")
		self.nameStringLE = QtGui.QLineEdit()
		self.nameStringLE.setMaximumWidth(200)
		nameStringLayout.addWidget(nameStringLbl)
		nameStringLayout.addWidget(self.nameStringLE)

		self.executeLayout = QtGui.QHBoxLayout()
		self.executeLayout.addLayout(nameStringLayout)
		self.executeSwitchBtn = QtGui.QPushButton('Build the FK to IK System')
		self.executeSwitchBtn.clicked.connect(self.switchBuild)
		self.executeSwitchBtn.setToolTip("Please hit the big green button when all the rest of the options are filled out, and it will hopefully build you an FK to IK switch system.")
		self.executeSwitchBtn.setMinimumHeight(80)
		self.executeSwitchBtn.setMinimumWidth(670)
		self.executeSwitchBtn.setStyleSheet("background-color: green")
		self.executeLayout.addWidget(self.executeSwitchBtn)

		topUIVLayout.addLayout(rigHLayout)
		topUIVLayout.addLayout(self.executeLayout)

		self.setGeometry(300, 300, 815, 610)
		self.setWindowTitle('FK to IK Switch')    
		self.show()

	def checkAllSelections(self,mySel):
		validSelection = True
		if not checkRepeatSelection(mySel, self.fkJointList, "FK Joints") : validSelection = False
		if not checkRepeatSelection(mySel, self.ikJointList, "IK Joints") : validSelection = False
		if not checkRepeatSelection(mySel, self.masterJointList, "Master Joints") : validSelection = False
		if not checkRepeatSelection(mySel, self.fkCtrlList, "FK Controls", isJoint=False) : validSelection = False
		if not checkRepeatSelection(mySel, self.ikCtrlList, "IK Controls", isJoint=False) : validSelection = False
		if not checkRepeatSelection(mySel, [self.masterCtrl], "Master Control", isJoint=False) : validSelection = False
		return validSelection

	def fkJointBtnPress(self):
		self.clearFkJoints()
		mySel = cmds.ls(sl=True)
		if jointSelectionFilter() and self.checkAllSelections(mySel):
			myFKJoints = JointHierarchy(mySel[0],mySel[1])
			self.fkJointList = myFKJoints.getJoints()
			print "FK Joint List " + str(self.fkJointList)
			self.fkJointTw.setJoints(self.fkJointList)

	def ikJointBtnPress(self):
		self.clearIkJoints()
		mySel = cmds.ls(sl=True)
		if jointSelectionFilter() and self.checkAllSelections(mySel):
			mySel = cmds.ls(sl=True)
			myIKJoints = JointHierarchy(mySel[0],mySel[1])
			self.ikJointList = myIKJoints.getJoints()
			self.ikJointTw.setJoints(self.ikJointList)

	def masterJointBtnPress(self):
		self.clearMasterJoints()
		mySel = cmds.ls(sl=True)
		if jointSelectionFilter() and self.checkAllSelections(mySel):
			mySel = cmds.ls(sl=True)
			myMasterJoints = JointHierarchy(mySel[0],mySel[1])
			self.masterJointList = myMasterJoints.getJoints()
			self.masterJointTw.setJoints(self.masterJointList)

	def fkCtrlBtnPress(self):
		"""Function to filter through the selection, make sure that we do not have any joints and add the remaining items to the Ctrls List"""
		self.clearFkCtrls()
		mySel = cmds.ls(sl=True)
		if ctrlSelectionFilter() and self.checkAllSelections(mySel):
			mySel = cmds.ls(sl=True)
			for ctrl in mySel:
				treeItem = QtGui.QTreeWidgetItem(ctrl)
				treeItem.setText(0, ctrl)
				treeItem.setFlags(QtCore.Qt.ItemIsEnabled) #Set the Item so it cannot be selected
				self.fkCtrlsTw.addTopLevelItem(treeItem)
				self.fkCtrlList.append(ctrl)

	def ikCtrlBtnPress(self):
		"""Function to filter through the selection, make sure that we do not have any joints and add the remaining items to the Ctrls List"""
		self.clearIkCtrls()
		mySel = cmds.ls(sl=True)
		if ctrlSelectionFilter() and self.checkAllSelections(mySel):
			mySel = cmds.ls(sl=True)
			for ctrl in mySel:
				treeItem = QtGui.QTreeWidgetItem(ctrl)
				treeItem.setText(0, ctrl)
				treeItem.setFlags(QtCore.Qt.ItemIsEnabled) #Set the Item so it cannot be selected
				self.ikCtrlsTw.addTopLevelItem(treeItem)
				self.ikCtrlList.append(ctrl)

	def masterCtrlBtnPress(self):
		"""Function to filter through the selection, make sure that we do not have any joints and add the remaining items to the Ctrls List"""
		self.clearMasterCtrl()
		mySel = cmds.ls(sl=True)
		if ctrlSelectionFilter() and self.checkAllSelections(mySel):
			if len(mySel) == 1:
				self.masterCtrl = mySel[0]
				masterAtts = cmds.listAttr(mySel[0], s=True, r=True, w=True, c=True, userDefined=True) #This will give a list of readable, keyable, scalar, user defined attributes
				for att in masterAtts:
					treeItem = QtGui.QTreeWidgetItem(att)
					treeItem.setText(0, att)
					self.masterCtrlTw.addTopLevelItem(treeItem)
					self.masterCtrlAtts.append(att)
			else: cmds.warning("Please select a single node that has user defined attributes added, to act as the Master Control")

	def clearFkJoints(self):
		self.fkJointTw.clear()
		self.fkJointList = []

	def clearIkJoints(self):
		self.ikJointTw.clear()
		self.ikJointList = []

	def clearMasterJoints(self):
		self.masterJointTw.clear()
		self.masterJointList = []

	def clearFkCtrls(self):
		self.fkCtrlsTw.clear()
		self.fkCtrlList = []

	def clearIkCtrls(self):
		self.ikCtrlsTw.clear()
		self.ikCtrlList = []

	def clearMasterCtrl(self):
		self.masterCtrlTw.clear()
		self.masterCtrl = None
		self.masterCtrlAtts = []
		self.masterCtrlAtt = None

	def checkMasterCtrlAtt(self):
		self.masterCtrlAtt = None
		if self.masterCtrlTw.currentItem():
			self.masterCtrlAtt = self.masterCtrlTw.currentItem().text(0)

	def switchSetupCheck(self):
		validSetup = True
		self.checkMasterCtrlAtt()
		if len(self.fkJointList) == 0:
			cmds.warning("You need to specify the FK Joints")
			validSetup = False
		if len(self.ikJointList) == 0:
			cmds.warning("You need to specify the IK Joints")
			validSetup = False
		if len(self.masterJointList) == 0:
			cmds.warning("You need to specify the Master Joints")
			validSetup = False		
		if len(self.fkCtrlList) == 0:
			cmds.warning("You need to specify the FK Controls")
			validSetup = False	
		if len(self.ikCtrlList) == 0:
			cmds.warning("You need to specify the IK Controls")
			validSetup = False	
		if not self.masterCtrlAtt:
			cmds.warning("You need to specify the Master Control Attribute")
			validSetup = False
		if not self.masterCtrl:
			cmds.warning("You need to specify the Master Control")
			validSetup = False	
		if not (len(self.fkJointList) == len(self.ikJointList) ==  len(self.masterJointList)):
			cmds.warning("Incorrect Joint Numbers: You need to speciy the same number of FK, IK and Master Joints")
			validSetup = False
		print "name len",len(self.nameStringLE.text())
		if len(self.nameStringLE.text()) == 0:
			cmds.warning("No name string has been specificed")
			validSetup = False		
		return validSetup


	def jointParentConstraints(self):
		"""Function to set up the parent contraints on all of the joints"""
		for i, jnt in enumerate(self.masterJointList):
			parConstName = nameConstraintRebuild(jnt.getName(), self.nameStringLE.text(), "jnt",  "parC", nameEnd = (self.masterCtrlAtt + "Switch"))
			parConst = cmds.parentConstraint(self.fkJointList[i].getName(), self.ikJointList[i].getName(),jnt.getName(), name = parConstName)
			for i, att in enumerate(cmds.parentConstraint(parConstName, q=1, weightAliasList = True)):
				if i == 0: #Set first FK weight
					cmds.renameAttr(parConstName + "." + att , "fkWeight")
				elif i == 1: #Set Second IK Weight 
					cmds.renameAttr(parConstName + "." + att , "ikWeight")
				#Now we make the correct connections to control the weights
			cmds.connectAttr(self.masterCtrl + "." + self.masterCtrlAtt, parConstName + ".ikWeight")
			cmds.connectAttr(self.pmaSwitchNode + ".output1D", parConstName + ".fkWeight")

	def controlsVisibility(self):
		for ctrl in self.fkCtrlList:
			cmds.connectAttr(self.pmaSwitchNode + ".output1D", ctrl + ".visibility")
		for ctrl in self.ikCtrlList:
			cmds.connectAttr(self.masterCtrl + "." + self.masterCtrlAtt, ctrl + ".visibility")

	def switchBuild(self):
		if self.switchSetupCheck():
			#Close Undo Chunk
			cmds.undoInfo(openChunk=True)			
			self.pmaSwitchNode = None
			self.checkMasterCtrlAtt()
			pMAName = nameSwitchRebuild(self.masterCtrl, "cv", "pma", nameEnd = self.masterCtrlAtt + "Switch")
			myRigPm = cmds.shadingNode('plusMinusAverage', asUtility=True, name= pMAName)
			self.pmaSwitchNode = myRigPm
			cmds.setAttr(self.pmaSwitchNode + ".operation", 2)
			cmds.setAttr(self.pmaSwitchNode + ".input1D[0]", 1)
			print "MasterStuff :",self.masterCtrl,self.masterCtrlAtt
			cmds.connectAttr(self.masterCtrl + "." + self.masterCtrlAtt, self.pmaSwitchNode + ".input1D[1]")
			#Now we have the switch, lets add the joint Parent Constraints
			self.jointParentConstraints()
			#Now implement all the ctrl; visibility
			self.controlsVisibility()
			cmds.undoInfo(closeChunk=True)

			
if __name__ == "__main__":
	fred = FRFKtoIKSwitchUI()
