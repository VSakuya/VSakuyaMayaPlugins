import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.cmds as cmds

# Plug-in information:
kPluginCmdName          = 'vsaDeselectSpecial'

# Deselect per component, if dpc = 2 means deselect half, dpc = 3 means deselcect 1/3
kDeselectPerComFlag     = '-dpc'
kDeselectPerComLongFlag = '-deselectPerComponent'
defaultDeselectPerCom   = 2
# Delta means deselect selected object by index 0,1,2,etc., if d >= dpc, it will be error
kDeltaFlag              = '-d'
kDeltaLongFlag          = '-delta'
defaultDelta            = 0

# Special deselect main function
class DeselectSpecialCommand( OpenMayaMPx.MPxCommand):
    def __init__(self):
        ''' Constructor '''
        OpenMayaMPx.MPxCommand.__init__(self)

    def parseArgs(self, pArgs):
        # set default arguments
        global defaultDeselectPerCom
        self.deselectPerCom = defaultDeselectPerCom
        global  defaultDelta
        self.delta = defaultDelta

        # Obtain the flag value, if the flag is set
        argData = OpenMaya.MArgParser( self.syntax(), pArgs )
        if argData.isFlagSet( kDeselectPerComFlag ):
            flagValue = argData.flagArgumentInt( kDeselectPerComFlag, 0 )
            if flagValue > defaultDeselectPerCom:
                self.deselectPerCom = flagValue

        if argData.isFlagSet( kDeltaFlag ):
            flagValue = argData.flagArgumentInt( kDeltaFlag, 0 )
            # dpc must >= delta + 1
            if flagValue + 1 > self.deselectPerCom:
                cmds.error("Delta has to lower than Deselect per component minus 1!")
            if flagValue > defaultDelta:
                self.delta = flagValue

    def doIt( self, args ):
        ''' Command Execution '''

        # Parse the passed arguments
        self.parseArgs( args )

        # Create an instance of MDagModifier to keep track of the created objects,
        # and to undo their creation in our undoIt() function
        self.dagModifier = OpenMaya.MDagModifier()
        self.createWindow()

    # Special select implement
    def specialDeselect(self):
        cmds.selectPref(trackSelectionOrder=True)
        getSelection = cmds.ls(selection=True, flatten=True)

        if len(getSelection) < self.deselectPerCom:
            cmds.error("the number of components selected must greater than Deselect per component")

        for i in range(len(getSelection)):
            if i % self.deselectPerCom == self.delta:
                cmds.select(getSelection[i], deselect=True)

    # Window for control
    def createWindow(self):
        self.window = "DSCWindow"
        self.title = "Special Deselect"
        self.size = (400, 200)

        # close old window is open
        if cmds.window(self.window, exists=True):
            cmds.deleteUI(self.window, window=True)

        # create new window
        self.window = cmds.window(self.window, title=self.title, widthHeight=self.size)

        cmds.columnLayout(adjustableColumn=True)


        self.dscIntInput = cmds.intSliderGrp(field=True, label='Deselect per component: ',
                                        minValue=2, value=self.deselectPerCom)

        global defaultDelta
        self.deltaIntInput = cmds.intSliderGrp(field=True, label='Delta: ',
                                        minValue=0, value=self.delta)
        self.dscActionBtn = cmds.button(label='Special Deselect', command=self.dscAction)

        # display new window
        cmds.showWindow()

    # Define the action of Special Deselect button
    def dscAction(self, args):
        dsc = cmds.intSliderGrp(self.dscIntInput, query=True, value=True)
        delta = cmds.intSliderGrp(self.deltaIntInput, query=True, value=True)
        self.deselectPerCom = dsc
        # dpc must >= delta + 1
        if delta + 1 > self.deselectPerCom:
            cmds.error("Delta has to lower than Deselect per component minus 1!")
        self.delta = delta
        self.specialDeselect()

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
    return OpenMayaMPx.asMPxPtr(DeselectSpecialCommand())

def syntaxCreator():
    ''' Defines the argument and flag syntax for this command. '''
    syntax = OpenMaya.MSyntax()
    syntax.addFlag(kDeselectPerComFlag, kDeselectPerComLongFlag, OpenMaya.MSyntax.kDouble)
    syntax.addFlag(kDeltaFlag, kDeltaLongFlag, OpenMaya.MSyntax.kDouble)
    return syntax


def initializePlugin(mobject):
    ''' Initializes the plug-in. '''
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.registerCommand(kPluginCmdName, cmdCreator, syntaxCreator)
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


















