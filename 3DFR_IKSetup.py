"""IK SETUP - MAYA 2015

#====================================================
#
# DEVELOPMENT HISTORY
#               
#       
# TO DO
#               - Add in UI to help specify Search String! At the moment this is lamely HardCoded  - FIX THIS NOW!             
#               - Complete Tool Tips
#               - Record Help Video of tool Set
#
#====================================================
# GUIDE
#               - Use the Conventional naming system for this Rig kit - ex: "spider00_jnt_r_fronty00_leg_ik"
#               - Select the start IK joint, and then the End IK joint where you want the IK system to finish
#               - Then select the group of the IK Control that you want to mark the end of the IK system. Naming Convention "spider00_grp_rotCtrl"
#               - Optionally you can then select the group of the control that you want to act as the Pole vector
#
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

def jointNameCheck(jointName, nameSearchString):
    validName = True
    if (len(jointName.split("_jnt_"))) == 1:
        validName = False
        print "ERROR - Exiting tool, since \"_jnt_\" is not in the joint naming convention for " + jointName
    if (len(jointName.split(nameSearchString))) == 1:
        validName = False
        print "ERROR - Exiting tool, since \"" + nameSearchString + "\" is not in the joint naming convention for " + jointName
    return validName



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




##############################Check that we have valid Joint Names########################################
def checkJointNames(jntList, searchStringName):
    validJointNames = True

    for jnt in jntList:
        if not jointNameCheck(jnt, searchStringName):
            validJointNames = False
    return validJointNames

###########################Check that we have a valid selection (based on count)#############################
# def checkSelectionCount(mySelectionCount):
#     validSelectionCount = False
#     if (mySelectionCount == 3):
#         validSelectionCount = True
#         myCtrlGrp = mySel[mySelectionCount-1] #This is going to be the Control that is duplicated - MAKE SURE THE CONTROL GROUP IS SELECTED LAST!
#     elif (mySelectionCount == 4):
#         validSelectionCount = True
#         myCtrlGrp = mySel[mySelectionCount-2] #This is going to be the Control that is duplicated - MAKE SURE THE CONTROL GROUP IS SELECTED SECOND LAST!
#         myPoleVectorGrp = mySel[mySelectionCount-1] #This is going to be the Pole Vector Control that is duplicated - MAKE SURE THE CONTROL GROUP IS SELECTED LAST!

#     if not validSelectionCount: print "Error : Incorrect number of objects selected. Please select the start joint, the end joint, and the master controller and optionally the Pole Vector Ctrl group that you want to assign"
#     return validSelectionCount

#######################################Check we have a valid Control Group########################################
def checkValidControlGrp(ctrlGrp, controlType):
    validCtrlGroup = False
    if "Ctrl" in ctrlGrp:
        grpChild = cmds.listRelatives(ctrlGrp, children=True)
        #print grpChild #Finds Transform
        grpCurveChild = cmds.listRelatives(grpChild[0], children=True)
        #print grpCurveChild
        grpCurveShape = cmds.ls(grpCurveChild, type="nurbsCurve")
        #print grpCurveShape
        if len(grpCurveShape) != 0:
            #print "We have a valid Control"
            validCtrlGroup = True
        else: print "No valid " + controlType + " Selected"
    else:
        print "No valid " + controlType + " Selected"
    return validCtrlGroup



# if (mySelectionCount == 3 and validSelectionCount and validJointNames and validCtrlGroup) or (mySelectionCount == 4 and validSelectionCount and validJointNames and validCtrlGroup and validPoleGroup):
#     #All conditions are met, we can now continue to build the IK system
#     print "Success"
#     newIKName = nameRebuild(myJnts[1], searchStringName, "jnt", "ikh")
#     newEffName = nameRebuild(myJnts[1], searchStringName, "jnt", "eff")
#     newLocName  = nameRebuild(myJnts[1], searchStringName, "jnt", "loc")
#     newIK = cmds.ikHandle(sj=myJnts[0], ee=myJnts[1], solver='ikRPsolver', name = newIKName)
#     IKpos = cmds.xform(newIK[0], q=True, t=True, ws=True)
#     newLoc = cmds.spaceLocator(name=newLocName)
#     cmds.xform(newLoc, ws=True, t=IKpos)
#     cmds.rename(newIK[1], newEffName)
#     tempConst = cmds.parentConstraint(newLoc,newIK[0]) #Parent the IKHandle to the Locator
#     #Now craete the new controller to control this section
#     newCtrlPack = cmds.duplicate(myCtrlGrp, renameChildren=True)
#     newGrpName = nameRebuild(jnt, searchStringName, "jnt", "grp")
#     newCtrlName = nameRebuild(jnt, searchStringName, "jnt", "cv")
#     cmds.rename(newCtrlPack[0], newGrpName)
#     cmds.rename(newCtrlPack[1], newCtrlName)
#     #myNewCtrlGrps.append(newGrpName)
#     #print "My new Ctrl is : " + str(newGrpName)
#     tempConst = cmds.parentConstraint(newIKName,newGrpName)
#     cmds.delete(tempConst) #Delete the temporary constraint
#     #Sonow correctly parent Constrain the Joint to the control
#     cmds.parentConstraint(cmds.listRelatives(newGrpName, children=True)[0],newLoc)
    
#     if validPoleGroup:
#         newPoleCtrlPack = cmds.duplicate(myPoleVectorGrp, renameChildren=True)
#         newPoleGrpName  = nameRebuild(myJnts[1], searchStringName, "jnt", "grp","pole_ctrl")
#         newPoleCtrlName  = nameRebuild(myJnts[1], searchStringName, "jnt", "cv","pole_ctrl")
#         cmds.rename(newPoleCtrlPack[0], newPoleGrpName)
#         cmds.rename(newPoleCtrlPack[1], newPoleCtrlName)
#         tempConst = cmds.pointConstraint(myJnts[0],myJnts[1],newPoleGrpName)   
#         cmds.delete(tempConst) #Delete the temporary constraint
#         #Now we need to find the second joint down the chain so we can figure out how to move out the PoleVector
#         secondJnt = cmds.listRelatives(myJnts[0], children=True)[0]
#         jointPos = cmds.xform(secondJnt, q=True, t=True, ws=True)
#         print str(jointPos)
#         newPoleGrpPos = cmds.xform(newPoleGrpName, q=True, t=True, ws=True)
#         posDiff = [jointPos[0] - newPoleGrpPos[0],jointPos[1] - newPoleGrpPos[1],jointPos[2] - newPoleGrpPos[2]]
#         cmds.xform(newPoleGrpName, ws=True, t=[jointPos[0] + posDiff[0],jointPos[1] + posDiff[1],jointPos[2] + posDiff[2]])
#         #newLoc = cmds.spaceLocator(name=newLocName)
#         #cmds.xform(newLoc, ws=True, t=jointPos)
#         cmds.poleVectorConstraint(newPoleCtrlName, newIKName)

        
#     else:
#         print "Not going to build Pole Vector"
       
# else:
#     print "The intiial selection is wrong. We cannot continue"




######################################################################################################
#====================================================
#   Create IK Setup UI
#====================================================


class TDFR_IKSetup_Ui(MayaQWidgetDockableMixin, QtGui.QDialog):
    """Class to block out all the main functionality of the IKSetup UI"""
    def __init__(self):
        super(TDFR_IKSetup_Ui, self).__init__()
        self.CtrlGrp = None
        self.poleGrp = None
        self.searchStringName = None #This is the UI descriptor

        masterIKFrame = QtGui.QFrame(self) # Create frame and Layout to hold all the User List View
        masterIKFrame.setFrameShape(QtGui.QFrame.StyledPanel)
        topUIVLayout = QtGui.QVBoxLayout(masterIKFrame)

        nameStringLbl = QtGui.QLabel("Please select the start and end joint of the IK system you want to setup.\nThen please select the group of the Control and/or PoleVector Control. \n-----------------------------\nPlease name descriptor:")
        nameStringLbl.setToolTip("Joints should have naming convention: \"spider00_jnt_r_front00_leg_ik\" - In this case the descriptor is \"front\"\nMain IK control should have naming convention: \"spider00_grp_iKCtrl\"\nPole Vector Control should have naming convention: \"spider00_grp_pVCtrl" )

        self.nameStringLE = QtGui.QLineEdit()
        self.nameStringLE.setMaximumWidth(300)
        topUIVLayout.addWidget(nameStringLbl)
        topUIVLayout.addWidget(self.nameStringLE)

        self.executeSwitchBtn = QtGui.QPushButton('Build the IK System')
        self.executeSwitchBtn.clicked.connect(self.buildIKSetup)
        self.executeSwitchBtn.setToolTip("Please hit the big green button when all the rest of the options are filled out, and it will hopefully build you an IK system.")
        self.executeSwitchBtn.setMinimumHeight(80)
        self.executeSwitchBtn.setMinimumWidth(300)
        self.executeSwitchBtn.setStyleSheet("background-color: green")
        topUIVLayout.addWidget(self.executeSwitchBtn)

        self.setGeometry(385, 200, 815, 610)
        self.setWindowTitle('IK Setup')    
        self.show()


    def buildIKSetup(self):
        """Method to do the complete IK setup, starting with selection checks and then moving on to construction"""
        self.CtrlGrp = None
        self.poleGrp = None
        self.searchStringName = self.nameStringLE.text()

        # self.searchStringName = lineedit
        mySel = cmds.ls(sl = True)
        mySelectionCount = len(mySel)
        #print mySel

        myCtrlGrp = None 
        myPoleVectorGrp = None
        myJnts = cmds.ls(mySel, type = "joint") #This is going to be the Joint that is controlled
        print "my Joints : ", myJnts
        print "my Sel : ",  mySel

        validSelection = True
        if not checkJointNames(myJnts, self.searchStringName): validSelection = False
        
        validSelectionCount = False
        if (mySelectionCount < 3):
            print "Error : Too few  objects selected. Please select the start joint, the end joint, and the master controller and optionally the Pole Vector Ctrl group that you want to assign"
        elif (mySelectionCount == 3):
            validSelectionCount = True
            self.ctrlGrp = mySel[mySelectionCount-1] #This is going to be the Control that is duplicated - MAKE SURE THE CONTROL GROUP IS SELECTED LAST!
        elif (mySelectionCount == 4):
            validSelectionCount = True
            self.ctrlGrp = mySel[mySelectionCount-2] #This is going to be the Control that is duplicated - MAKE SURE THE CONTROL GROUP IS SELECTED SECOND LAST!
            self.poleGrp = mySel[mySelectionCount-1] #This is going to be the Pole Vector Control that is duplicated - MAKE SURE THE CONTROL GROUP IS SELECTED LAST!
        elif (mySelectionCount > 4):
            print "Error : Too many objects selected. Please select the start joint, the end joint, and the master controller and optionally the Pole Vector Ctrl group that you want to assign"

        if not validSelectionCount: 
            print "Error : Incorrect number of objects selected. Please select the start joint, the end joint, and the master controller and optionally the Pole Vector Ctrl group that you want to assign"
            validSelection = False

        if validSelection:
            #Now check the control groups for the main IK control and the pole vector
            if not checkValidControlGrp(self.ctrlGrp, "Control Group"): validSelection = False
            if not checkValidControlGrp(self.poleGrp, "Pole Vector Group"): validSelection = False

        if validSelection:
            #All conditions are met, we can now continue to build the IK system
            print "Success"
            newIKName = nameRebuild(myJnts[1], self.searchStringName, "jnt", "ikh")
            newEffName = nameRebuild(myJnts[1], self.searchStringName, "jnt", "eff")
            newLocName  = nameRebuild(myJnts[1], self.searchStringName, "jnt", "loc")
            newIK = cmds.ikHandle(sj=myJnts[0], ee=myJnts[1], solver='ikRPsolver', name = newIKName)
            IKpos = cmds.xform(newIK[0], q=True, t=True, ws=True)
            newLoc = cmds.spaceLocator(name=newLocName)
            cmds.xform(newLoc, ws=True, t=IKpos)
            cmds.rename(newIK[1], newEffName)
            tempConst = cmds.parentConstraint(newLoc,newIK[0]) #Parent the IKHandle to the Locator
            #Now craete the new controller to control this section
            newCtrlPack = cmds.duplicate(self.ctrlGrp, renameChildren=True)
            newGrpName = nameRebuild(myJnts[1], self.searchStringName, "jnt", "grp")
            newCtrlName = nameRebuild(myJnts[1], self.searchStringName, "jnt", "cv")
            cmds.rename(newCtrlPack[0], newGrpName)
            cmds.rename(newCtrlPack[1], newCtrlName)
            #myNewCtrlGrps.append(newGrpName)
            #print "My new Ctrl is : " + str(newGrpName)
            tempConst = cmds.parentConstraint(newIKName,newGrpName)
            cmds.delete(tempConst) #Delete the temporary constraint
            #Sonow correctly parent Constrain the Joint to the control
            cmds.parentConstraint(cmds.listRelatives(newGrpName, children=True)[0],newLoc)
            
            if self.poleGrp:
                if cmds.objExists(self.poleGrp):
                    newPoleCtrlPack = cmds.duplicate(self.poleGrp, renameChildren=True)
                    newPoleGrpName  = nameRebuild(myJnts[1], self.searchStringName, "jnt", "grp","pole_ctrl")
                    newPoleCtrlName  = nameRebuild(myJnts[1], self.searchStringName, "jnt", "cv","pole_ctrl")
                    cmds.rename(newPoleCtrlPack[0], newPoleGrpName)
                    cmds.rename(newPoleCtrlPack[1], newPoleCtrlName)
                    tempConst = cmds.pointConstraint(myJnts[0],myJnts[1],newPoleGrpName)   
                    cmds.delete(tempConst) #Delete the temporary constraint
                    #Now we need to find the second joint down the chain so we can figure out how to move out the PoleVector
                    secondJnt = cmds.listRelatives(myJnts[0], children=True)[0]
                    jointPos = cmds.xform(secondJnt, q=True, t=True, ws=True)
                    print str(jointPos)
                    newPoleGrpPos = cmds.xform(newPoleGrpName, q=True, t=True, ws=True)
                    posDiff = [jointPos[0] - newPoleGrpPos[0],jointPos[1] - newPoleGrpPos[1],jointPos[2] - newPoleGrpPos[2]]
                    cmds.xform(newPoleGrpName, ws=True, t=[jointPos[0] + posDiff[0],jointPos[1] + posDiff[1],jointPos[2] + posDiff[2]])
                    #newLoc = cmds.spaceLocator(name=newLocName)
                    #cmds.xform(newLoc, ws=True, t=jointPos)
                    cmds.poleVectorConstraint(newPoleCtrlName, newIKName)

                
            else:
                print "Not going to build Pole Vector"
#====================================================
#   Class for inheriting TDFR_IKSetup_Ui
#====================================================   

class Main_Ui(TDFR_IKSetup_Ui):
    def __init__(self):
        super(Main_Ui, self).__init__()
        self.setDockableParameters(dockable = True, width = 385, height = 200)

#====================================================
#   Function for creating UI, only runs in standalone
#====================================================           

if __name__ == "__main__":
    # try:
    Main_Ui().show()
    # except:
    #   pass
