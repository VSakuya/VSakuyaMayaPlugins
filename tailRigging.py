import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.cmds as cmds

# Intro: Simple plugin for tail-like rigging
# Plug-in information:
kPluginCmdName = 'vsaTailRigging'

# Command function
class TailRiggingCommand( OpenMayaMPx.MPxCommand ):
    def __init__(self):
        ''' Constructor '''
        OpenMayaMPx.MPxCommand.__init__(self)

    def doIt( self, args ):
        ''' Command Execution '''
        self.dagModifier = OpenMaya.MDagModifier()

        # Create working window
        self.createWindow()

    # Tail rigging implement
    def tailRigging(self, namePrefix, numOfSpans, ctrllerSize):
        # Get all joints with start and end
        getSelection = cmds.ls(selection=True)
        startJoint = getSelection[0]
        endEffector = getSelection[len(getSelection) - 1]

        # Get first joint orientation
        # WARNING: root joint rotate must be (0,0,0) and all joints on tail must keep in one line
        tmpJoint = startJoint
        # Get all parent joint orientation for getting orientaion of the first joint
        parentJoints = [startJoint]
        while tmpJoint != None:
            tmpParent = cmds.listRelatives(tmpJoint, p=True)
            if tmpParent:
                tmpType = cmds.objectType(tmpParent)
                if tmpType == 'joint':
                    parentJoints.append(tmpParent[0])
            tmpJoint = tmpParent
        finalOrient = [0, 0, 0]
        for item in parentJoints:
            tmpOrient = cmds.getAttr(item + '.jointOrient')
            finalOrient[0] = finalOrient[0] + tmpOrient[0][0]
            finalOrient[1] = finalOrient[1] + tmpOrient[0][1]
            finalOrient[2] = finalOrient[2] + tmpOrient[0][2]

        # startOrient = cmds.getAttr(getSelection[0] + '.jointOrient')[0]
        startPerpendicular = [0, finalOrient[1] + 90, finalOrient[2]]

        # Create IK
        # Example: [u'ikHandle1', u'effector1', u'curve1']
        ikResult = cmds.ikHandle(sj=startJoint, ee=endEffector, sol='ikSplineSolver', pcv=False, ns=3)
        ctrlCurve = ikResult[2]

        # Rebulid curve for setting spans
        cmds.rebuildCurve(ctrlCurve, s=numOfSpans)

        # Get all CV
        cvCount = cmds.getAttr(ctrlCurve + '.spans') + cmds.getAttr(ctrlCurve + '.degree')
        cvList = []
        for i in range(cvCount):
            cvList.append(ctrlCurve + '.cv[' + str(i) + ']')

        # Create clusters
        clusterList = []
        for i in range(len(cvList)):
            newClusterName = namePrefix + 'cluster_' + str(i - 1) + '_'
            # Ignore degrees
            if i == 0 or i == 1 or i == len(cvList) - 1:
                pass
            elif i == len(cvList) - 2:
                newCluster = cmds.cluster([cvList[len(cvList) - 1], cvList[len(cvList) - 2]], n=newClusterName)
                clusterList.append(newCluster[1])
            else:
                newCluster = cmds.cluster(cvList[i], n=newClusterName)
                clusterList.append(newCluster[1])

        # List of all controllers
        ctrllerList = []
        for i in range(len(clusterList)):
            # Get cluster world translation
            tmpPos = cmds.xform(clusterList[i], q=True, ws=True, piv=True)
            tmpPos = [tmpPos[0], tmpPos[1], tmpPos[2]]

            # Create controllers
            newCtrllerName = namePrefix + 'ctrller_' + str(i + 1)
            newCtrller = cmds.circle(n=newCtrllerName, r=ctrllerSize)
            # Center pivot
            newCtrllerCenter = cmds.objectCenter(newCtrller[0], gl=True)
            cmds.xform(newCtrller, pivots=newCtrllerCenter, ws=True)
            # Move and rotate controller to transform that perpendicular to first joint
            cmds.setAttr(newCtrller[0] + '.translate', tmpPos[0], tmpPos[1], tmpPos[2])
            cmds.setAttr(newCtrller[0] + '.rotate', startPerpendicular[0], startPerpendicular[1], startPerpendicular[2])
            # Freeze transform
            cmds.makeIdentity(newCtrller, apply=True)
            # Make constraint with clusters
            cmds.parentConstraint(newCtrller, clusterList[i])
            ctrllerList.append(newCtrller[0])

        # Make Hierarchy
        for i in range(len(ctrllerList)):
            if i != len(ctrllerList) - 1:
                cmds.parent(ctrllerList[i + 1], ctrllerList[i])

    # Window for control
    def createWindow(self):
        self.window = "TRWindow"
        self.title = "Quick Tail Rigging"
        self.size = (400, 200)

        # close old window is open
        if cmds.window(self.window, exists=True):
            cmds.deleteUI(self.window, window=True)

        # create new window
        self.window = cmds.window(self.window, title=self.title, widthHeight=self.size)

        cmds.columnLayout(adjustableColumn=True)
        cmds.separator()
        self.namePrefixInput = cmds.textFieldGrp(label='Name Prefix: ', text='name_')
        cmds.separator()
        self.numOfSpansInput = cmds.intSliderGrp(field=True, label='Number of Spans: ',
                                        minValue=1, value=4)

        self.ctrllerSizeInput = cmds.floatSliderGrp(field=True, label='Size of Controllers: ',
                                                    value=1.0)
        self.applyActionBtn = cmds.button(label='Apply', command=self.btnAction)

        # display new window
        cmds.showWindow()

    # Define the action of Special Deselect button
    def btnAction(self, args):
        namePrefix = cmds.textFieldGrp(self.namePrefixInput, q=True, text=True)
        numOfSpans = cmds.intSliderGrp(self.numOfSpansInput, query=True, value=True)
        ctrllerSize = cmds.floatSliderGrp(self.ctrllerSizeInput, query=True, value=True)

        self.tailRigging(namePrefix, numOfSpans, ctrllerSize)


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
    return OpenMayaMPx.asMPxPtr(TailRiggingCommand())

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


















