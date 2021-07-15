import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.cmds as cmds

# Intro: Simple color changer for curve
# Plug-in information:
kPluginCmdName = 'vsaCurveColorChanger'

# Special deselect main function
class CurveColorChangerCommand( OpenMayaMPx.MPxCommand ):
    def __init__(self):
        ''' Constructor '''
        OpenMayaMPx.MPxCommand.__init__(self)

    def doIt( self, args ):
        ''' Command Execution '''

        # Create an instance of MDagModifier to keep track of the created objects,
        # and to undo their creation in our undoIt() function
        self.dagModifier = OpenMaya.MDagModifier()
        self.createWindow()

    # Color changer implement
    def curveColorChanger(self, object, color):
        cmds.setAttr(object + '.overrideEnabled', 1)
        cmds.setAttr(object + '.overrideRGBColors', 1)
        rgb = ("R", "G", "B")
        for channel, color in zip(rgb, color): 
            cmds.setAttr(object + ".overrideColor%s" % channel, color)

    # Window for control
    def createWindow(self):
        self.window = "CCCWindow"
        self.title = "Curve Color Changer"
        self.size = (200, 100)

        # close old window is open
        if cmds.window(self.window, exists=True):
            cmds.deleteUI(self.window, window=True)

        # create new window
        self.window = cmds.window(self.window, title=self.title, widthHeight=self.size)

        cmds.columnLayout(adjustableColumn=True)
        
        cmds.separator()
        self.colorInput = cmds.colorSliderGrp(label='Curve Color: ')
        cmds.separator(height=20, width=100)
        self.applyActionBtn = cmds.button(label='Apply', command=self.btnAction)

        # display new window
        cmds.showWindow()

    # Define the action of Special Deselect button
    def btnAction(self, args):
        color = cmds.colorSliderGrp(self.colorInput, q=True, rgb=True)
        getSelection = cmds.ls(selection=True)
        print (getSelection)
        if len(getSelection) > 0:
            for item in getSelection:
                self.curveColorChanger(item, color)


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
    return OpenMayaMPx.asMPxPtr(CurveColorChangerCommand())

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


















