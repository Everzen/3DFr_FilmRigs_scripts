"""Create Flip controller - MAYA 2015

#====================================================
#
# DEVELOPMENT HISTORY
#               
#       
# TO DO
#               - This version is terrible and hacky. Need UI with axis flip choice
#				- Needs to also adjust names - maybe basic search and replace for _l_ etc 
#
#
# RECENT FEATURES 
#
#
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



import maya.cmds as cmds

mySel = cmds.ls(sl=True, type="transform")
print mySel
cmds.select( clear=True )
#Create empty Group
flipGrp = cmds.createNode( 'transform', name=mySel[0]+"_flipOre")
print flipGrp
#Find current Contoller Pos
ctrlGroupPos = cmds.xform(mySel[0], q=1, ws=True, rp=True)
#Move Group to the right position
cmds.xform(flipGrp, t=ctrlGroupPos, ws=True)
newCtrl = cmds.duplicate(mySel)[0]
cmds.parent(newCtrl, flipGrp)
cmds.setAttr(flipGrp + ".scaleX", -1)