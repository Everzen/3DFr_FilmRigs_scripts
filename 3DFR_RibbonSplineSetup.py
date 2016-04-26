"""RIBBON SPLINE TOOL - MAYA 2015

#====================================================
#
# DEVELOPMENT HISTORY
#				- Some tool Tips added.
#		
# TO DO
#				- Complete Tool Tips
#				- Record Help Video of tool Set
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


from PySide import QtCore, QtGui
import maya.cmds as cmds
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from maya.OpenMaya import MVector
#import numpy as np



#Function for Rebuilding Names
def nameRebuild(name,searchString,typeToReplace, replaceWith, nameAddition = "ctrl"):
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
                  
    newName = newName + nameAddition
    return newName

#Function for Rebuilding Names
def nameBase(name,searchString,typeToReplace, replaceWith):
	"""Function to strip out just the start of the name, so we can add stuff"""
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
	                newName = newName + searchString + "_"
	                # return newName
	            else:
	                newName = newName + nameEle + "_"
	return newName


class ribbonMarker(object):
	"""A class to setup the marker with all the properties it needs to be build the ribbon spline"""
	def __init__(self, name, index):
		self.name = name
		self.index = index
		self.skinJoint = False
		self.secCtrl = False
		self.primaryCtrl = False
		self.alignedMarker = None
		self.pos = None
		self.uParameter = None
		self.hairFollicle = None

	def getName(self):
		return self.name

	def getIndex(self):
		return self.index

	def isSkinJoint(self):
		return self.skinJoint

	def isSecCtrl(self):
		return self.secCtrl

	def isPrimaryCtrl(self):
		return self.primaryCtrl

	def setSkinJoint(self, bool):
		self.skinJoint = bool

	def setSecCtrl(self, bool):
		self.secCtrl = bool

	def setPrimaryCtrl(self, bool):
		self.primaryCtrl = bool

	def getAlignedMarker(self):
		return self.alignedMarker

	def setAlignedMarker(self, marker):
		self.alignedMarker = marker
		markerPos =  cmds.xform(marker, t=True, q=True, ws=True)
		self.setPos(markerPos)

	def getPos(self):
		return self.pos
	
	def setPos(self, newPos):
		self.pos = newPos 

	def getUParameter(self):
		return self.uParameter

	def setUParameter(self, uParam):
		self.uParameter = uParam

	def getHairFollicle(self):
		return self.hairFollicle

	def setHairFollicle(self, hairFol):
		self.hairFollicle = hairFol

	def update(self, guideSpline):
		"""Function to check the current marker position and update self.pos to its new value"""
		if self.alignedMarker:
			markerPos =  cmds.xform(self.alignedMarker, t=True, q=True, ws=True)
			self.setPos(markerPos)
			#Now work out the UParam
			newPara = cmds.closestPointOnCurve(guideSpline, ip=markerPos, paramU=True) #Create node to calculate uParam
			newParaVal = cmds.getAttr(newPara + ".paramU")
			cmds.delete(newPara)
			self.setUParameter(newPara)
		else:
			print "Warning - Cannot set Aligned Marker Position, because the marker has not been defined"



#====================================================
#	Ribbon Spline Creation Class
#====================================================
class RibbonSpline(object):
	"""Class for creating a ribbon spline system"""
	def __init__(self, totalMarkerList, secCtrlList, primaryCtrlList, searchString):
		self.totalMarkerList = [] #This list gathers the markers and 
		self.sortMarkerList(totalMarkerList, secCtrlList, primaryCtrlList)
		#Specify the controllers that we are going to assign
		self.primaryControlGroup = None
		self.secondaryControlGroup = None

		self.searchString = searchString #Thisni the descriptor name that we can use to break down names and rename things correctly
		#Create a list of parts to collect to be deleted at the end if needed
		self.tempGuideParts = []
		self.tempConstructionParts = []
		self.ribbonParts = []

		#Now we want to create 
		self.guideSpline = None
		#self.buildGuideSpline()

		self.guideNurbsRibbon = None
		#self.buildNurbsRibbon()

		#Setup all the Hair Follicles
		self.ribbonHairFollicles = []
		#self.addHairFollicles()

		#Now that we have all the hair follicles run through all the markers, and add the appropriate controls
		self.primaryJointRibbonList = [] 
		self.skinJointGrpList = []
		#self.addRibbonAllJointsControls()

	def sortMarkerList(self, totalMarkerList, secCtrlList, primaryCtrlList):
		"""Method to sort the totalMarkerList into skinJoints, secondary Controls and Primary Controls"""
		self.totalMarkerList = [] #Clear Out Total Marker List

		for i, loc in enumerate(totalMarkerList):
			newMarker =  ribbonMarker(loc, i)
			newMarker.setSkinJoint(True)   #Set Skin Joint to be True and turn this off if we find out it is a control
			for ctrl in secCtrlList:
				if loc == ctrl: #We have found a secondary Ctrl
					newMarker.setSecCtrl(True)
					newMarker.setSkinJoint(False)
			for ctrl in primaryCtrlList:
				if loc == ctrl: #We have found a primary Ctrl
					newMarker.setPrimaryCtrl(True)
			self.totalMarkerList.append(newMarker)


	def buildGuideSpline(self):
		cPoints = []
		for marker in self.totalMarkerList:
			markerPos = cmds.xform(marker.getName(), t=True, q=True, ws=True)
			cPoints.append(markerPos)
		nameStart = nameBase(self.totalMarkerList[0].getName(), self.searchString, "loc", "cv")
		guideSplineName = nameStart + "ribbonGuideSpline"
		self.guideSpline = cmds.curve(editPoint = cPoints, degree=3, name=guideSplineName)       #Need to add Naming Convention here
		self.tempGuideParts.append(self.guideSpline)

		for i, marker in enumerate(self.totalMarkerList):
			locPos = cmds.xform(marker.getName(), t=True, q=True, ws=True)
			newPara = cmds.closestPointOnCurve(self.guideSpline, ip=locPos, paramU=True)
			newParaVal = cmds.getAttr(newPara + ".paramU")
			cmds.delete(newPara)
			# print "new ParaVal : ", newParaVal
			##Now Create a new Locator and add it to the precise parameter position
			nameStart = nameRebuild(marker.getName(), self.searchString, "loc", "loc",nameAddition = "tempRibbonGuide")
			newAlignedLoc = cmds.spaceLocator(name = nameStart) 
			# guideSplineName = nameStart + "ribbonGuideSpline"                                         #Need naming convention
			self.tempGuideParts.append(newAlignedLoc[0])
			mPath = cmds.pathAnimation(newAlignedLoc, follow=True, c=self.guideSpline)
			uAnimNode = cmds.listConnections(mPath + ".uValue", source=True) 
			cmds.delete(uAnimNode)
			cmds.setAttr(mPath + ".uValue", newParaVal)
			self.totalMarkerList[i].setAlignedMarker(newAlignedLoc[0])
			self.totalMarkerList[i].setUParameter(newParaVal)


	def updateMarkers(self):
		for marker in self.totalMarkerList: marker.update()



	def buildNurbsRibbon(self):
		if self.guideSpline:
			guideDeg = cmds.getAttr(self.guideSpline + '.degree' )
			guideSpan = cmds.getAttr(self.guideSpline + '.spans' )
			oneCurvePoints = []
			otherCurvePoints = []
			for i in xrange(guideDeg + guideSpan):
				cvPos = cmds.pointPosition(self.guideSpline + '.cv[' + str(i) + "]", w=True )
				newPara = cmds.closestPointOnCurve(self.guideSpline, ip=cvPos, paramU=True)  #Find the parameter Value
				newParaVal = cmds.getAttr(newPara + ".paramU")
				cmds.delete(newPara)
				infoNode = cmds.pointOnCurve(self.guideSpline, ch=True, pr=newParaVal)  #Now find the Position and tangent!
				posy = (cmds.getAttr(infoNode + ".position"))[0]  # returns the position
				posy = MVector(posy[0],posy[1],posy[2])
				normy = (cmds.getAttr(infoNode + ".tangent"))[0]
				normy = MVector(normy[0],normy[1],normy[2]) #Use MVector from maya.openMaya
				normy = normy.normal()
				vertVect = MVector(0,1,0)
				sideMove = normy^vertVect #This is the notation for a cross product. Pretty cool. Should be a normal movement
				sideMove = sideMove.normal() * 0.5
				sideMovePos = posy + sideMove 
				otherSideMovePos = posy - sideMove
				oneCurvePoints.append([sideMovePos[0],sideMovePos[1],sideMovePos[2]])
				otherCurvePoints.append([otherSideMovePos[0],otherSideMovePos[1],otherSideMovePos[2]])

			oneSideCurve = cmds.curve(editPoint = oneCurvePoints, degree=3)
			OtherSideCurve = cmds.curve(editPoint = otherCurvePoints, degree=3)
			self.tempConstructionParts.append(oneSideCurve)
			self.tempConstructionParts.append(OtherSideCurve)
			#Now we loft the surface between the two Curves!
			nameStart = nameBase(self.totalMarkerList[0].getName(), self.searchString, "loc", "nbs")
			nameStart += "ribbonSurface"
			self.guideNurbsRibbon = cmds.loft(oneSideCurve, OtherSideCurve, name = nameStart, constructionHistory = True, uniform = True, close = False, autoReverse = True, degree = 3, sectionSpans = 1, range = False, polygon = 0, reverseSurfaceNormals = True)
			self.guideNurbsRibbon = self.guideNurbsRibbon[0]
			self.ribbonParts.append(self.guideNurbsRibbon)
			#ribbonShape = (cmds.listRelatives(ribbonSurface, children=True, shapes=True))[0]


	def addHairFollicles(self):
		ribbonShape = (cmds.listRelatives(self.guideNurbsRibbon, children=True, shapes=True))[0]
		uCoordinates = []
		for marker in self.totalMarkerList:
			# print "Alignedmarker : ", marker.getAlignedMarker()
			markerPos = cmds.xform(marker.getAlignedMarker(), t=True, q=True, ws=True)
			cPS = cmds.createNode("closestPointOnSurface")
			cmds.connectAttr(ribbonShape + ".local", cPS + ".inputSurface", force=True)
			cmds.connectAttr(marker.getAlignedMarker() + ".translate", cPS + ".inPosition", force=True)
			uCoord = cmds.getAttr(cPS + ".parameterU")
			# print "My UCord : ", uCoord
			uCoordinates.append(uCoord)
			cmds.delete(cPS)

		ribbonSurfaceMaxU = cmds.getAttr(self.guideNurbsRibbon + ".maxValueU") #Find the maximum U Parameter, so we can start spacing out the HairFollicles
		self.ribbonHairFollicles = []
		#Now create follicles and attach them to the surface! 
		for x, uCoord in enumerate(uCoordinates):
			uParaPos = 1/ribbonSurfaceMaxU*uCoord
			grpNameStart = nameRebuild(self.totalMarkerList[x].getName(), self.searchString, "loc", "grp", nameAddition = "hairFol")
			hFolNameStart = nameRebuild(self.totalMarkerList[x].getName(), self.searchString, "loc", "hFol", nameAddition = "splineFollicle")
			hFol_transform = cmds.createNode("transform", name=grpNameStart)             
			hFol = cmds.createNode("follicle", parent = hFol_transform, name=hFolNameStart)                        
			self.ribbonParts.append(hFol)
			self.ribbonParts.append(hFol_transform)
			#cmds.parent(ribbonSplineFollicleName + str(x), ribbonSplineFollicleGroupName)
			cmds.connectAttr(ribbonShape + ".local", hFol + ".inputSurface", force=True)
			cmds.connectAttr(ribbonShape + ".worldMatrix[0]",hFol + ".inputWorldMatrix", force=True)
			cmds.connectAttr(hFol + ".outRotate", hFol_transform +  ".rotate", force=True)
			cmds.connectAttr(hFol + ".outTranslate", hFol_transform + ".translate", force=True)
			cmds.setAttr(hFol + ".parameterV", 0.5)
			cmds.setAttr(hFol + ".parameterU", uParaPos)
			self.ribbonHairFollicles.append(hFol_transform)
			self.totalMarkerList[x].setHairFollicle(hFol_transform) #specify each of the Hair follicles in the markers
		
		nameStart = nameBase(self.totalMarkerList[0].getName(), self.searchString, "loc", "nbs")
		nameStart += "ribbonFollicles"		
		hairGrp = cmds.createNode("transform", name = nameStart)                               
		self.ribbonParts.append(hairGrp)
		cmds.parent(self.ribbonHairFollicles, hairGrp)
		cmds.setAttr(hairGrp + ".inheritsTransform", 0)


	def addSkinJoint(self, marker):
		"""Method to generate basic Skin joints without any controls"""
		grpNameStart = nameRebuild(marker.getName(), self.searchString, "loc", "grp", nameAddition = "skinOre")
		jntNameStart = nameRebuild(marker.getName(), self.searchString, "loc", "jnt", nameAddition = "skin")
		newGrp = cmds.createNode("transform", name=grpNameStart)                       
		skinJnt = cmds.joint(name=jntNameStart)                                        
		cmds.parentConstraint(marker.getHairFollicle(), newGrp)
		self.ribbonParts.append(newGrp)
		self.ribbonParts.append(skinJnt)
		self.skinJointGrpList.append(newGrp)



	def addSecRibbonControl(self, marker):
		"""Method to generate secondary Ribbon Controllers"""
		grpNameStart = nameRebuild(marker.getName(), self.searchString, "loc", "grp", nameAddition = "skinOre")
		jntNameStart = nameRebuild(marker.getName(), self.searchString, "loc", "jnt", nameAddition = "skin")
		newGrp = cmds.createNode("transform", name=grpNameStart)                      
		skinJnt = cmds.joint(name=jntNameStart)
		ctrlGrpNameStart = nameRebuild(marker.getName(), self.searchString, "loc", "grp", nameAddition = "ribbonSecCtrlOre")
		ctrlNameStart = nameRebuild(marker.getName(), self.searchString, "loc", "cv", nameAddition = "ribbonSecCtrl")		
		newCtrlPack = (cmds.duplicate(self.secondaryControlGroup, renameChildren=True))    
		cmds.rename(newCtrlPack[0], ctrlGrpNameStart)
		cmds.rename(newCtrlPack[1], ctrlNameStart)		
		tempConst = cmds.parentConstraint(skinJnt,ctrlGrpNameStart)
		cmds.delete(tempConst) #Delete the temporary constraint
		cmds.parentConstraint(cmds.listRelatives(ctrlGrpNameStart, children=True)[0],skinJnt)
		cmds.parentConstraint(marker.getHairFollicle(), ctrlGrpNameStart)
		self.ribbonParts.append(ctrlGrpNameStart)
		self.ribbonParts.append(skinJnt)
		self.ribbonParts.append(newGrp)

	def addPrimaryRibbonControl(self, marker):
		"""Method to generate secondary Ribbon Controllers"""
		grpNameStart = nameRebuild(marker.getName(), self.searchString, "loc", "grp", nameAddition = "ribbonBindOre")
		jntNameStart = nameRebuild(marker.getName(), self.searchString, "loc", "jnt", nameAddition = "ribbonBind")		
		newGrp = cmds.createNode("transform", name=grpNameStart)                       #NEED TO ADD SOME NAMING 
		ctrlRibbonJnt = cmds.joint(name=jntNameStart)
		ctrlGrpNameStart = nameRebuild(marker.getName(), self.searchString, "loc", "grp", nameAddition = "ribbonPrimCtrlOre")
		ctrlNameStart = nameRebuild(marker.getName(), self.searchString, "loc", "cv", nameAddition = "ribbonPrimCtrl")		
		newCtrlPack = (cmds.duplicate(self.primaryControlGroup, renameChildren=True))    #HARDCODED CTRL EXAMPLE
		cmds.rename(newCtrlPack[0], ctrlGrpNameStart)
		cmds.rename(newCtrlPack[1], ctrlNameStart)			
		tempConst = cmds.parentConstraint(newGrp,ctrlGrpNameStart)
		cmds.delete(tempConst) #Delete the temporary constraint
		cmds.parentConstraint(cmds.listRelatives(ctrlGrpNameStart, children=True)[0],ctrlRibbonJnt)
		tempConst = cmds.parentConstraint(marker.getHairFollicle(), ctrlGrpNameStart)
		cmds.delete(tempConst) #Delete the temporary constraint
		self.primaryJointRibbonList.append(ctrlRibbonJnt)
		self.ribbonParts.append(ctrlGrpNameStart)
		self.ribbonParts.append(ctrlRibbonJnt)
		self.ribbonParts.append(newGrp)

	def addRibbonAllJointsControls(self):
		"""Method to step through all the markers and add the appropriate skinJoint, secondary Control or Primary Control"""
		self.primaryJointRibbonList = []
		for marker in self.totalMarkerList:
			if marker.isSkinJoint(): self.addSkinJoint(marker)
			if marker.isSecCtrl(): self.addSecRibbonControl(marker)
			if marker.isPrimaryCtrl(): self.addPrimaryRibbonControl(marker)
		#Now we skin the primary controls to the Ribbon Spline Nurbs surface
		nameStart = nameBase(self.totalMarkerList[0].getName(), self.searchString, "loc", "sCl")
		nameStart += "ribbonBind"		
		cmds.skinCluster(self.primaryJointRibbonList, self.guideNurbsRibbon, toSelectedBones = True, name=nameStart)
		#Now group all the skin joints together

		nameStart = nameBase(self.totalMarkerList[0].getName(), self.searchString, "loc", "grp")
		nameStart += "ribbonJntBind"				
		jointGrp = cmds.createNode("transform", name = nameStart)
		self.ribbonParts.append(jointGrp)
		cmds.parent(self.skinJointGrpList, jointGrp)
		cmds.setAttr(jointGrp + ".inheritsTransform", 0)

		cmds.delete(self.tempConstructionParts)
		self.tempConstructionParts = []

	def buildRibbonFromGuideSpline(self):
		self.buildNurbsRibbon()  #First add the nurbs surface
		self.addHairFollicles()  #Add in the Hair Follicles
		self.addRibbonAllJointsControls() #Add in the controls and skin joints

	def cleanUpAfterRibbon(self):
		cmds.delete(self.tempConstructionParts)
		self.tempConstructionParts = []
		cmds.delete(self.tempGuideParts)
		self.tempGuideParts = []

	def deleteGuideSpline(self):
		if len(self.tempConstructionParts) != 0: 
			cmds.delete(self.tempConstructionParts)
			self.tempConstructionParts = []
		if len(self.tempGuideParts) != 0:
			cmds.delete(self.tempGuideParts)
			self.tempGuideParts = []

	def deleteRibbonSpline(self):
		if len(self.ribbonParts) != 0:
			cmds.delete(self.ribbonParts)
			self.ribbonParts = []

	def getPrimaryController(self):
		return self.primaryControlGroup

	def setPrimaryController(self, ctrlGroup):
		self.primaryControlGroup = ctrlGroup

	def getSecondaryController(self):
		return self.secondaryControlGroup

	def setSecondaryController(self, ctrlGroup):
		self.secondaryControlGroup = ctrlGroup




######################################################################################################
#====================================================
#	Create Ribbon Spline UI
#====================================================

class RibbonSpline_Ui(MayaQWidgetDockableMixin, QtGui.QDialog):
	"""Class to carry all the functionality for the RibbonSpline UI"""
	def __init__(self):
		super(RibbonSpline_Ui, self).__init__()
		self.ribbonSpline = None
		self.selection = []
		self.noCtrlList = []        #A list to 
		self.secCtrlList = []
		self.primaryCtrlList = []
		self.primaryCtrlGrp = None
		self.secondaryCtrlGroup = None
		self.setWindowFlags(QtCore.Qt.Tool)
		self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
		self.setWindowTitle("RPJ/PJC/ST - Ribbon Spline Tool")
		masterLayout = QtGui.QVBoxLayout()
		self.head_LAB = QtGui.QLabel("Ribbon Spline Tool")
		font = QtGui.QFont()
		font.setPointSize(14)
		font.setBold(True)
		font.setWeight(75)
		self.head_LAB.setFont(font)
		self.head_LAB.setAlignment(QtCore.Qt.AlignCenter)
		masterLayout.addWidget(self.head_LAB)
		self.orderPanel()
		masterLayout.addLayout(self.orderPanelLayout)
		self.mainButtons()
		masterLayout.addLayout(self.mainButtonsLayout)
		self.connections()
		self.setLayout(masterLayout)

	#====================================================
	#	Create order panel widget
	#====================================================

	def orderPanel(self):
		self.orderPanelLayout = QtGui.QHBoxLayout()
		self.noCtrlPanelLayout = QtGui.QVBoxLayout()
		self.ribbonObjs_LV = QtGui.QListWidget()
		self.ribbonObjs_LV.setToolTip("The nodes here should be locator transforms that mark the positions along the Ribbon Spline. There should also be the Primary Controller and Secondary Controller Group.\nAll nodes can then be dragged right to the appropriate areas.\n Example locator naming convention: \"spider00_loc_r_front00_foot\" - This convention must be followed\n Example Controller naming convention: \"spider00_grp_rotCtrl\" - his convention must be followed ")
		self.ribbonObjs_LV.setDragEnabled(True)
		self.ribbonObjs_LV.setDragDropMode(QtGui.QAbstractItemView.DragDrop)
		self.ribbonObjs_LV.setDefaultDropAction(QtCore.Qt.MoveAction)
		self.ribbonObjs_LV.setAlternatingRowColors(True)
		self.ribbonObjs_LV.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
		self.ribbonObjs_LV.setMinimumWidth(145)
		self.noCtrlPanelLayout.addWidget(self.ribbonObjs_LV)
		self.noCtrl_LAB = QtGui.QLabel("Ribbon Objects")
		self.noCtrlPanelLayout.addWidget(self.noCtrl_LAB)

		self.secondaryPanelLayout = QtGui.QVBoxLayout()
		self.secCtrl_LV = QtGui.QListWidget()
		self.secCtrl_LV.setDragEnabled(True)
		self.secCtrl_LV.setDragDropMode(QtGui.QAbstractItemView.DragDrop)
		self.secCtrl_LV.setDefaultDropAction(QtCore.Qt.MoveAction)
		self.secCtrl_LV.setAlternatingRowColors(True)
		self.secCtrl_LV.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
		self.secCtrl_LV.setMinimumWidth(145)
		self.secondaryPanelLayout.addWidget(self.secCtrl_LV)
		self.secondary_LAB = QtGui.QLabel("Secondary Controls")
		self.secondaryPanelLayout.addWidget(self.secondary_LAB)

		self.primaryPanelLayout = QtGui.QVBoxLayout()
		self.primaryCtrl_LV = QtGui.QListWidget()
		self.primaryCtrl_LV.setDragEnabled(True)
		self.primaryCtrl_LV.setDragDropMode(QtGui.QAbstractItemView.DragDrop)
		self.primaryCtrl_LV.setDefaultDropAction(QtCore.Qt.MoveAction)
		self.primaryCtrl_LV.setAlternatingRowColors(True)
		self.primaryCtrl_LV.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
		self.primaryCtrl_LV.setMinimumWidth(145)
		self.primaryPanelLayout.addWidget(self.primaryCtrl_LV)
		self.primary_LAB = QtGui.QLabel("Primary Controls")
		self.primaryPanelLayout.addWidget(self.primary_LAB)

		self.controlPanelLayout = QtGui.QVBoxLayout()
		self.primaryCtrlType_LV = QtGui.QListWidget()
		self.primaryCtrlType_LV.setDragEnabled(True)
		self.primaryCtrlType_LV.setDragDropMode(QtGui.QAbstractItemView.DragDrop)
		self.primaryCtrlType_LV.setDefaultDropAction(QtCore.Qt.MoveAction)
		self.primaryCtrlType_LV.setAlternatingRowColors(True)
		self.primaryCtrlType_LV.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)	
		self.primaryCtrlType_LV.setMinimumWidth(145)
		self.primaryCtrl_LAB = QtGui.QLabel("Primary Control Group")
		self.secondaryCtrlType_LV = QtGui.QListWidget()
		self.secondaryCtrlType_LV.setDragEnabled(True)
		self.secondaryCtrlType_LV.setDragDropMode(QtGui.QAbstractItemView.DragDrop)
		self.secondaryCtrlType_LV.setDefaultDropAction(QtCore.Qt.MoveAction)
		self.secondaryCtrlType_LV.setAlternatingRowColors(True)
		self.secondaryCtrlType_LV.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
		self.secondaryCtrlType_LV.setMinimumWidth(145)
		self.secondaryCtrl_LAB = QtGui.QLabel("Secondary Control Group")
		self.controlPanelLayout.addWidget(self.primaryCtrlType_LV)
		self.controlPanelLayout.addWidget(self.primaryCtrl_LAB)
		self.controlPanelLayout.addWidget(self.secondaryCtrlType_LV)
		self.controlPanelLayout.addWidget(self.secondaryCtrl_LAB)

		self.orderPanelLayout.addLayout(self.noCtrlPanelLayout)
		self.orderPanelLayout.addLayout(self.secondaryPanelLayout)
		self.orderPanelLayout.addLayout(self.primaryPanelLayout)
		self.orderPanelLayout.addLayout(self.controlPanelLayout)

	# ====================================================
	# 	Create main buttons widget
	# ====================================================

	def mainButtons(self):
		self.mainButtonsLayout = QtGui.QVBoxLayout()

		selectionButtonsLayout = QtGui.QHBoxLayout()
		self.loadMarkers_BTN = QtGui.QPushButton("Add In Markers and Controls")
		self.loadMarkers_BTN.setToolTip("Please select the locators that you want to use to mark the Ribbon Spline positions. Then select the group of the Primary Controller sample \n and the group of the secondary Controller sample. Then press this button.\n Example locator naming convention: \"spider00_loc_r_front00_foot\" - This convention must be followed\n Example Controller naming convention: \"spider00_grp_rotCtrl\" - his convention must be followed")
		self.loadMarkers_BTN.setMinimumWidth(145)
		self.loadMarkers_BTN.setMaximumWidth(145)
		selectionButtonsLayout.addWidget(self.loadMarkers_BTN)
		self.clearMarkers_BTN = QtGui.QPushButton("Clear Markers and Controls")
		self.clearMarkers_BTN.setMinimumWidth(145)
		self.clearMarkers_BTN.setMaximumWidth(145)
		selectionButtonsLayout.addWidget(self.clearMarkers_BTN)
		nameStringLbl = QtGui.QLabel("        Please name descriptor:")
		nameStringLbl.setMinimumWidth(145)
		self.nameStringLE = QtGui.QLineEdit()
		self.nameStringLE.setToolTip("This is the string descriptor that will allow the tool to separate out the sequence of points along the spline.\n For example, is locators are called \"spider00_loc_r_front00_foot\" then the string \"front\" should be written here.")
		self.nameStringLE.setMinimumWidth(145)
		selectionButtonsLayout.addWidget(nameStringLbl)
		selectionButtonsLayout.addWidget(self.nameStringLE)

		selectionButtonsLayout.addStretch()

		controlButtonsLayout = QtGui.QHBoxLayout()
		self.buildGuideSpline_BTN = QtGui.QPushButton("Create Guide Spline")
		self.buildGuideSpline_BTN.setToolTip("This button generates a guide spline with guide locators placed along it. The spline can be adjusted to correct the alignment of the locators.\n The locators can also be repositioned using their motion path along the spline. Final locator positions will represent final skin joint and controller positions.")
		self.buildGuideSpline_BTN.setMinimumWidth(145)
		self.buildGuideSpline_BTN.setMaximumWidth(145)
		controlButtonsLayout.addWidget(self.buildGuideSpline_BTN)
		self.deleteSpline_BTN = QtGui.QPushButton("Delete Guide Spline")
		self.deleteSpline_BTN.setMinimumWidth(145)
		self.deleteSpline_BTN.setMaximumWidth(145)
		controlButtonsLayout.addWidget(self.deleteSpline_BTN)
		controlButtonsLayout.addStretch()

		buildRibbonLayout = QtGui.QVBoxLayout()
		self.buildRibbonSpline_BTN = QtGui.QPushButton("BUILD A RIBBON SPLINE")
		self.buildRibbonSpline_BTN.setMinimumHeight(80)
		self.buildRibbonSpline_BTN.setToolTip("Please hit the big green button when all the rest of the options are filled out, and it will hopefully \n build you")
		self.buildRibbonSpline_BTN.setStyleSheet("background-color: green")		# self.buildRibbonSpline_BTN.setMinimumWidth(145)
		# self.buildRibbonSpline_BTN.setMaximumWidth(145)
		buildRibbonLayout.addWidget(self.buildRibbonSpline_BTN)
		self.deleteRibbonSpline_BTN = QtGui.QPushButton("Delete Ribbon Spline")
		# self.deleteRibbonSpline.setMinimumWidth(145)
		# self.deleteRibbonSpline.setMaximumWidth(145)
		buildRibbonLayout.addWidget(self.deleteRibbonSpline_BTN)
		buildRibbonLayout.addStretch()

		self.mainButtonsLayout.addLayout(selectionButtonsLayout)
		self.mainButtonsLayout.addLayout(controlButtonsLayout)
		self.mainButtonsLayout.addLayout(buildRibbonLayout)

	# #====================================================
	# #	Create connections between buttons and their methods
	# #====================================================

	def connections(self):#connect buttons to functions
		###Example: self.Select_Items_BTN.clicked.connect(self.Select_Items)
		self.loadMarkers_BTN.clicked.connect(self.loadSelection)
		self.clearMarkers_BTN.clicked.connect(self.clearSelection)
	# 	self.demote_BTN.clicked.connect(self.demote)
	# 	self.promote_BTN.clicked.connect(self.promote)
		self.buildGuideSpline_BTN.clicked.connect(self.buildGuideSpline)
		self.deleteSpline_BTN.clicked.connect(self.deleteGuideSpline)
		self.buildRibbonSpline_BTN.clicked.connect(self.buildRibbonSpline)
		self.deleteRibbonSpline_BTN.clicked.connect(self.deleteRibbonSpline)

	# #====================================================
	# #	Method for loading selected objects into the UI
	# #====================================================

	def loadSelection(self):
		self.clearSelection()
		self.selection = cmds.ls(shortNames = True, selection = True)
		for item in self.selection:
			QtGui.QListWidgetItem(item, self.ribbonObjs_LV)


	# #====================================================
	# #	Method for clearing all nodes from the UI
	# #====================================================

	def clearSelection(self):
		self.selection = []
		self.ribbonObjs_LV.clear()
		self.secCtrl_LV.clear()
		self.primaryCtrl_LV.clear()
		self.primaryCtrlType_LV.clear()
		self.secondaryCtrlType_LV.clear()

	def locatorFilter(self, objList):
		locatorList = []
		for o in objList:
			shap = cmds.listRelatives(o, children=True, shapes=True)
			if shap: #Shap can be "None" if no results are returned (group has no shapes)
				for s in shap:
					if cmds.nodeType(s) == "locator":
						locatorList.append(o)
		return locatorList

	
	def collectCtrls(self):
		self.noCtrlList = []
		for i in xrange(self.ribbonObjs_LV.count()): self.noCtrlList.append(self.ribbonObjs_LV.item(i).text())  #Collect the text for all the no control items
		self.secCtrlList = []
		for i in xrange(self.secCtrl_LV.count()): self.secCtrlList.append(self.secCtrl_LV.item(i).text())  #Collect the text for all the secondary control items
		self.primaryCtrlList = []
		for i in xrange(self.primaryCtrl_LV.count()): self.primaryCtrlList.append(self.primaryCtrl_LV.item(i).text())  #Collect the text for all the no control items

		#filter out the locators to act as the markers
		self.noCtrlList =self.locatorFilter(self.noCtrlList)
		self.secCtrlList = self.locatorFilter(self.secCtrlList)
		self.primaryCtrlList = self.locatorFilter(self.primaryCtrlList)
		# self.secCtrlList = 
		# self.primaryCtrlList = 
		print "noCtrlList :", self.noCtrlList
		print "secCtrlList :", self.secCtrlList
		print "primaryCtrlList :", self.primaryCtrlList
		# self.clearSelection() #Clear out the tool after it has been built - delete options will still be allowed

	def buildGuideSpline(self):
		self.collectCtrls()
		#filter out locators & use these as the marker points for the Ribbon Spline
		markers = self.locatorFilter(self.selection)
		validSetup = True
		if len(self.nameStringLE.text()) == 0:
			cmds.warning("No name/descriptor has been specified")
			validSetup = False	
		if validSetup:
				self.ribbonSpline = RibbonSpline(markers, self.secCtrlList, self.primaryCtrlList, self.nameStringLE.text())
				self.ribbonSpline.buildGuideSpline() #Build the Guide Spline

	def deleteGuideSpline(self):
		self.ribbonSpline.deleteGuideSpline()
			
	def buildRibbonSpline(self):
		#First of all Establish our Primary and Secondary Controls
		self.primaryCtrlGrp = None
		self.secondaryCtrlGroup = None

		validSetup = True

		if self.primaryCtrlType_LV.count() == 1:
			self.primaryCtrlGrp = self.primaryCtrlType_LV.item(0).text()
			self.ribbonSpline.setPrimaryController(self.primaryCtrlGrp)
		else:
			validSetup = False
			cmds.warning("Please only have a single primary control type specified")
		if self.secondaryCtrlType_LV.count() == 1:
			self.secondaryCtrlGrp = self.secondaryCtrlType_LV.item(0).text()
			self.ribbonSpline.setSecondaryController(self.secondaryCtrlGrp)
		else:
			validSetup = False
			cmds.warning("Please only have a single secondary control type specified")
		#Now check that a proper string name descriptor has been provided
		if len(self.nameStringLE.text()) == 0:
			cmds.warning("No name string has been specified")
			validSetup = False	

		if self.ribbonSpline: #Check we have a valid guide spline
			if validSetup: #Check we have valid controls to allow the build to begin
					self.ribbonSpline.buildRibbonFromGuideSpline()
		else:
			cmds.warning("Please Generate the Guide Spline first, then adjust if needed, before generating the full Ribbon Spline")

	def deleteRibbonSpline(self):
		if self.ribbonSpline:
			self.ribbonSpline.deleteRibbonSpline()


#====================================================
#	Class for inheriting RibbonSpline UI
#====================================================	

class Main_Ui(RibbonSpline_Ui):
	def __init__(self):
		super(Main_Ui, self).__init__()

		self.setDockableParameters(dockable = True, width = 0, height = 400)

#====================================================
#	Function for creating UI, only runs in standalone
#====================================================			

if __name__ == "__main__":
	# try:
	Main_Ui().show()
	# except:
	# 	pass

