"""Geometry Group Builder - MAYA 2015

#====================================================
#
# DEVELOPMENT HISTORY
#               
#       
# TO DO
#
#
#
# RECENT FEATURES 
#
#
#====================================================
# GUIDE
#			- This tool simply creates an identical transform to the geo, and then parents the geo under it, so that we can then rig to the geo
#
#
# IMPORTANT NOTES
#
###########################################################################################################################################################
"""
import maya.cmds as cmds


def nameBase(name,typeToReplace, replaceWith):
	"""Function just replace the object type with a new type in the name"""
	nameBits = name.split("_")
	newName = ""
	for i,bit in enumerate(nameBits):
	    if i != len(nameBits)-1:
	        newSplit = bit.split(typeToReplace)
	        if len(newSplit) != 1:
	            newName = newName + replaceWith + "_"
	        else:
	            newName = newName + bit + "_"
	    else:
	        newName = newName + bit
	        
	return newName


mySel = cmds.ls(sl=True, type="transform")[0]
# print mySel

newObj = cmds.duplicate(mySel)[0]
# print newObj
newShape = cmds.listRelatives(newObj, shapes=True)[0]
cmds.delete(newShape)

grpName = nameBase(mySel,"geo", "grp")

newGrpName = cmds.rename(newObj, grpName)

cmds.parent(mySel, newGrpName)
