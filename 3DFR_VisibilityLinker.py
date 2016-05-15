"""Visibility Linker - MAYA 2016

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
#               - Basic UI and functionality working. User can confirm, or abandon connections, when existing visibility connections are found
#
#====================================================
# GUIDE
#               - Load tool - select objects to control Visibility of and load them into left hand List view
#				- Select a single controller with extra user attributes and load into right List View
#				- Highlight required attribute and click the big green button
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
	if isJoint: checkList = [sJ.getName() for sJ in checkSwitchJointList] #Collect Names since we have switch Joints, we need names to comapre to the selection
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

#====================================================
#   Create Global Local Switch Setup for the Control - UI
#====================================================
class TDFR_VisibilityLinker_Ui(MayaQWidgetDockableMixin, QtGui.QDialog):
	"""Class to block out all the main functionality of the IKSetup UI"""
	def __init__(self):
		super(TDFR_VisibilityLinker_Ui, self).__init__()
		self.ctrlList = []
		self.visCtrl = None
		self.visCtrlAtts = []
		self.visCtrlAtt = None

		self.ctrlsTw = QtGui.QTreeWidget()
		self.ctrlsTw.setToolTip("Please select the controllers that you wish to link up the visibility for")
		self.ctrlsTw.setHeaderLabel("")
		self.ctrlsLbl = QtGui.QLabel("Specify Controllers to link visibility")
		self.ctrlsBtn = QtGui.QPushButton("Add Selected Control", self)
		self.ctrlsBtn.clicked.connect(self.ctrlBtnPress)
		self.ctrlsClearBtn = QtGui.QPushButton("Clear", self)
		self.ctrlsClearBtn.setMaximumWidth(40)
		self.ctrlsClearBtn.clicked.connect(self.clearCtrls)

		self.visCtrlTw = QtGui.QTreeWidget()
		self.visCtrlTw.setToolTip("Please select the controller that will control the visibility, and then highlight the attribute that you want to use to control the switch")
		self.visCtrlTw.setHeaderLabel("")
		self.visCtrlLbl = QtGui.QLabel("Please choose the visibility control Attribute")
		self.visCtrlBtn = QtGui.QPushButton("Add Selected Visibility Control", self)	
		self.visCtrlBtn.clicked.connect(self.visCtrlBtnPress)
		self.visCtrlClearBtn = QtGui.QPushButton("Clear", self)
		self.visCtrlClearBtn.setMaximumWidth(40)
		self.visCtrlClearBtn.clicked.connect(self.clearvisCtrl)

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
		switchButtonLayout.addWidget(self.visCtrlBtn)
		switchButtonLayout.addWidget(self.visCtrlClearBtn)
		switchLayout.addWidget(self.visCtrlLbl)
		switchLayout.addWidget(self.visCtrlTw)
		switchLayout.addLayout(switchButtonLayout)

		uiTopHLayout.addLayout(ctrlLayout)
		uiTopHLayout.addLayout(switchLayout)

		uiTotalLayout = QtGui.QVBoxLayout(masterSwitchFrame)
		uiTotalLayout.addLayout(uiTopHLayout)

		self.executeSwitchBtn = QtGui.QPushButton('Build Visibility Link for the Control/s')
		self.executeSwitchBtn.clicked.connect(self.visibilityLink)
		self.executeSwitchBtn.setToolTip("Please hit the big green button when all the rest of the options are filled out, and it will hopefully link up the visibilities of your controls.")
		self.executeSwitchBtn.setMinimumHeight(80)
		self.executeSwitchBtn.setMinimumWidth(470)
		self.executeSwitchBtn.setStyleSheet("background-color: green")
		uiTotalLayout.addWidget(self.executeSwitchBtn)

		self.setGeometry(300, 300, 550, 360)
		self.setWindowTitle('Visibility Linker')    
		self.show()


	def ctrlBtnPress(self):
		"""Function to filter through the selection, make sure that we do not have any joints and add the remaining items to the Ctrls List"""
		self.clearCtrls()
		mySel = cmds.ls(sl=True)
		if ctrlSelectionFilter() and self.checkAllSelections(mySel):
			mySel = cmds.ls(sl=True)
			if len(mySel) != 0:
				for ctrl in mySel:
					treeItem = QtGui.QTreeWidgetItem(ctrl)
					treeItem.setText(0, ctrl)
					treeItem.setFlags(QtCore.Qt.ItemIsEnabled) #Set the Item so it cannot be selected
					self.ctrlsTw.addTopLevelItem(treeItem)
					self.ctrlList.append(ctrl)
			else:
				cmds.warning("No Controllers Selected, please select the controls where you want to link visibility")


	def visCtrlBtnPress(self):
		"""Function to filter through the selection, make sure that we do not have any joints and add the remaining items to the Ctrls List"""
		self.clearvisCtrl()
		mySel = cmds.ls(sl=True)
		if ctrlSelectionFilter() and self.checkAllSelections(mySel):
			if len(mySel) == 1:
				self.visCtrl = mySel[0]
				masterAtts = cmds.listAttr(mySel[0], s=True, r=True, w=True, c=True, userDefined=True) #This will give a list of readable, keyable, scalar, user defined attributes
				for att in masterAtts:
					treeItem = QtGui.QTreeWidgetItem(att)
					treeItem.setText(0, att)
					self.visCtrlTw.addTopLevelItem(treeItem)
					self.visCtrlAtts.append(att)
			else: cmds.warning("Please select a single node that has user defined attributes added, to act as the Master Control")


	def checkAllSelections(self,mySel):
		validSelection = True
		if not checkRepeatSelection(mySel, self.ctrlList, "Controls", isJoint=False) : validSelection = False
		if not checkRepeatSelection(mySel, [self.visCtrl], "Switch Control", isJoint=False) : validSelection = False
		return validSelection

	def clearCtrls(self):
		self.ctrlsTw.clear()
		self.ctrlList = []

	def clearvisCtrl(self):
		self.visCtrlTw.clear()
		self.visCtrl = None
		self.visCtrlAtts = []
		self.visCtrlAtt = None

	def checkvisCtrlAtt(self):
		self.visCtrlAtt = None
		if self.visCtrlTw.currentItem():
			self.visCtrlAtt = self.visCtrlTw.currentItem().text(0)

	def visibilityLink(self):
		"""Method to loop through controls in the self.ctrlList, duplicate them and their groups and then create a Global/Local Switch"""
		repeatForAll = False
		abortOperation = False
		repeatBreakVisibility = False
		cmds.undoInfo(openChunk=True)		
		self.checkvisCtrlAtt()	

		for ctrl in self.ctrlList:	
			#Check to see if there is a connection to the visibility attribute
			visCon = cmds.listConnections(ctrl + ".visibility", d=False, s=True, p=True) #Returns the object name and the attribute
			if visCon: #This means that we have a connection, so check that we want to break it with an option box
				if not repeatForAll:
					breakConnection = True
					msgBox = QtGui.QMessageBox()
					msgBox.setText("The control " + ctrl + " already has it's visibility attributed connected.")
					msgBox.setInformativeText("Do you want to break this and override it?")
					msgBox.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.YesToAll | QtGui.QMessageBox.No | QtGui.QMessageBox.NoToAll)
					msgBox.setDefaultButton(QtGui.QMessageBox.Yes)
					msgResponse = msgBox.exec_()

					if msgResponse == QtGui.QMessageBox.Yes:
						print "Breaking Visibility Connection for : " + ctrl
						cmds.disconnectAttr(visCon[0], ctrl + ".visibility")
						cmds.connectAttr(self.visCtrl + "." + self.visCtrlAtt, ctrl + ".visibility")
					elif msgResponse == QtGui.QMessageBox.YesToAll:
						print "Breaking Visibility Connection for : " + ctrl
						repeatForAll = True
						repeatBreakVisibility = True
						cmds.disconnectAttr(visCon[0], ctrl + ".visibility")
						cmds.connectAttr(self.visCtrl + "." + self.visCtrlAtt, ctrl + ".visibility")
					elif msgResponse == QtGui.QMessageBox.No:
						breakConnection = False
						print "Aborting Visibility Connection for : " + ctrl
					elif msgResponse == QtGui.QMessageBox.NoToAll:
						repeatForAll = True
						repeatBreakVisibility = False
						breakConnection = False
						abortOperation = True
						print "Aborting Visibility Connection for : " + ctrl

				else: #We are in a repeat state
					if repeatBreakVisibility:
						print "Breaking Visibility Connection for : " + ctrl
						#We know to break the visibility connection everytime
						cmds.disconnectAttr(visCon[0], ctrl + ".visibility")
						cmds.connectAttr(self.visCtrl + "." + self.visCtrlAtt, ctrl + ".visibility")
			
			else: #There are no connections so just process the visibility unless we are aborting
				if not abortOperation:
					#Process connection of visibility
					print "Connecting Visibility for : " + ctrl
					cmds.connectAttr(self.visCtrl + "." + self.visCtrlAtt, ctrl + ".visibility")
				else:
					print "Aborting Visibility Connection for : " + ctrl



if __name__ == "__main__":
	TDFR_VisibilityLinker_Ui()
