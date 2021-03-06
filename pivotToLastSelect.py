import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.cmds as cmds

# Intro: Move Pivots to object center selected last
# Plug-in information:
kPluginCmdName = 'vsaPivotToLastSelect'

# Special deselect main function
class PivotToLastSelectCommand( OpenMayaMPx.MPxCommand):
    def __init__(self):
        ''' Constructor '''
        OpenMayaMPx.MPxCommand.__init__(self)

    def doIt( self, args ):
        ''' Command Execution '''

        # Create an instance of MDagModifier to keep track of the created objects,
        # and to undo their creation in our undoIt() function
        self.dagModifier = OpenMaya.MDagModifier()

        # Implement
        cmds.selectPref(trackSelectionOrder=True)
        getSelection = cmds.ls(selection=True, flatten=True)


        lastObejct = getSelection[len(getSelection) - 1]
        # Get type for transform
        lastType = cmds.objectType(lastObejct)

        if lastType == "transform":
            center = cmds.objectCenter(lastObejct, gl=True)
            for obj in getSelection:
                cmds.xform(obj, pivots=center, ws=True)
        else:
            pass

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
    return OpenMayaMPx.asMPxPtr(PivotToLastSelectCommand())

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


















