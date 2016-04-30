"""FK SETUP - MAYA 2015

#====================================================
#
# DEVELOPMENT HISTORY
#               
#       
# TO DO
#               - Complete Tool Tips
#               - Record Help Video of tool Set
#
# RECENT FEATURES 
#               - Undo Feature Added
#====================================================
# GUIDE
#               - Use the Conventional naming system for this Rig kit - ex: "spider00_jnt_r_fronty00_leg_ik"
#               - Select all the FK joints you want to setup FK controls for.
#               - Then select the group of the FK Control that you want to mark the end of the IK system. Naming Convention "spider00_grp_rotCtrl"
#
#
# IMPORTANT NOTES
#               - This setup does not deal with frozen transforms on objects. Make sure that all controls especially have not had transforms frozen
#
###########################################################################################################################################################
"""

import maya.cmds as cmds


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



def fKBuilder(nameSearchString):
    """Function to execute FK building given the nameSearchString, which it will get from the UI"""
    mySel = cmds.ls(sl = True)
    #print mySel
    
    
    myCtrlGrp = mySel[len(mySel)-1] #This is going to be the Control that is duplicated - MAKE SURE THE CONTROL GROUP IS SELECTED LAST!
    validCtrl = False
    myJnts = cmds.ls(mySel, type = "joint") #This is going to be the Joint that is controlled
    #print "my Joints : "  + str(myJnts)
     
    #print myCtrlGrp
    
    validJointNames = True
    
    for jnt in myJnts:
        if not jointNameCheck(jnt, nameSearchString):
            validJointNames = False
        
    if validJointNames:
        if "Ctrl" in myCtrlGrp:
            grpChild = cmds.listRelatives(myCtrlGrp, children=True)
            #print grpChild #Finds Transform
            grpCurveChild = cmds.listRelatives(grpChild[0], children=True)
            #print grpCurveChild
            grpCurveShape = cmds.ls(grpCurveChild, type="nurbsCurve")
            #print grpCurveShape
            if len(grpCurveShape) == 1:
                #print "We have a valid Control"
                validCtrl = True
            else: print "No valid Control Selected"
        else:
            print "No valid Control Selected"
        
        
        myNewCtrlGrps = []
        
        if validCtrl and (len(myJnts)) != 0:
            cmds.undoInfo(openChunk=True)           

            #We are good to go
            for jnt in myJnts:
                #print "My control is : " + myCtrlGrp
                newCtrlPack = (cmds.duplicate(myCtrlGrp, renameChildren=True))
                newGrpName = nameRebuild(jnt, nameSearchString, "jnt", "grp", nameAddition = "fkCtrl")
                newCtrlName = nameRebuild(jnt, nameSearchString, "jnt", "cv", nameAddition = "fkCtrl")
                cmds.rename(newCtrlPack[0], newGrpName)
                cmds.rename(newCtrlPack[1], newCtrlName)
                myNewCtrlGrps.append(newGrpName)
                #print "My new Ctrl is : " + str(newGrpName)
                tempConst = cmds.parentConstraint(jnt,newGrpName)
                cmds.delete(tempConst) #Delete the temporary constraint
                #Sonow correctly parent Constrain the Joint to the control
                parCName = nameRebuild(jnt, nameSearchString, "jnt", "parC", nameAddition = "fk")
                cmds.parentConstraint(cmds.listRelatives(newGrpName, children=True)[0],jnt, name = parCName)
        else: 
            print "Selection Error - Bad Control or No Joints Selected"
        
        #Now go through all the resulting controls and setup Parent Constrain relationships
        for i, ctrlGrp in enumerate(myNewCtrlGrps):
            if i != 0:
                parentCVCtrl = cmds.listRelatives(myNewCtrlGrps[i-1], children=True)[0]
                cmds.parentConstraint(parentCVCtrl,ctrlGrp,maintainOffset=True)
                
        cmds.select(mySel) #Return Selection to orginal before Tool Execution
        cmds.undoInfo(closeChunk=True)           


#####################################Basic UI Code############################################################################################import maya.cmds as cmds

class FKBuilderUI(object):
    def __init__(self):
        self.width = 360
        
        #if (cmds.window("FK Control Builder", exists=True))
        self.window = cmds.window(title="FK Control Builder", width = self.width)
                
        cmds.columnLayout()
        # Add controls to the Layout
        cmds.text( label='- Joint naming convention must follow ex: "spider00_jnt_r_side01_leg_fk"' )
        cmds.text( label='- Please select the joints you wnat to FK control"' )
        cmds.text( label='- Then select the master control group for the control you want to use"' )
        cmds.text( label='---------------------------------------------------------------------' )
        cmds.text( label='Search String' )
        self.searchText = cmds.textField(width = self.width, text="front")
        cmds.button(label="Build FK", width = self.width, command = lambda *args: fKBuilder(cmds.textField(self.searchText,q=True,tx=True)))
        
        # Display the window        
        cmds.showWindow()


try:
    #The deleteUI command will fail the first time, since the an instance of the FKBuilder Class does not exist. From then, it will close the window and work. Hacky.
    cmds.deleteUI(myFKBuilderUI.window)
except:
    print "Launching FK Builder"
myFKBuilderUI = FKBuilderUI()




