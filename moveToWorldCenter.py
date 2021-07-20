import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.cmds as cmds

# Intro: Move selected Objects to World Center (0, 0, 0) by pivot translation
# Plug-in information:
kPluginCmdName = 'vsaMoveToWorldCenter'

# Special deselect main function
class MoveToWorldCenterCommand( OpenMayaMPx.MPxCommand):
    def __init__(self):
        ''' Constructor '''
        OpenMayaMPx.MPxCommand.__init__(self)

    def doIt( self, args ):
        ''' Command Execution '''
        self.dagModifier = OpenMaya.MDagModifier()

        # Implement
        getSelection = cmds.ls(selection=True, flatten=True)
        for item in getSelection:
            pivP = cmds.xform(item,q=True, piv=True, ws=True)
            cmds.xform(item, t=(pivP[0] * -1, pivP[1] * -1,pivP[2] * -1), r=True)

    def isUndoable(self):
        ''' Determines whether or not this command is undoable within Maya. '''
        return True

    def redoIt(self):
        ''' Re-do the work of the command. '''
        self.dagModifier.doIt()

    def undoIt(self):
        ''' Undo the work performed by the command. '''
        self.dagModifier.undoIt()

##########################################################
# Plug-in initialization.
##########################################################
def cmdCreator():
    ''' Creates an instance of the command. '''
    return OpenMayaMPx.asMPxPtr(MoveToWorldCenterCommand())


def initializePlugin(mobject):
    ''' Initializes the plug-in. '''
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.registerCommand(kPluginCmdName, cmdCreator)
    except:
        sys.stderr.write('Failed to register command: ' + kPluginCmdName)
        raise


def uninitializePlugin(mobject):
    ''' Uninitializes the plug-in. '''
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterCommand(kPluginCmdName)
    except:
        sys.stderr.write('Failed to unregister command: ' + kPluginCmdName)
        raise


















