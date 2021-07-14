import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.cmds as cmds

# Plug-in information:
kPluginCmdName = 'vsaTailRigging'

# Special deselect main function
class TailRiggingCommand( OpenMayaMPx.MPxCommand ):
    def __init__(self):
        ''' Constructor '''
        OpenMayaMPx.MPxCommand.__init__(self)

    def doIt( self, args ):
        ''' Command Execution '''

        # Create an instance of MDagModifier to keep track of the created objects,
        # and to undo their creation in our undoIt() function
        self.dagModifier = OpenMaya.MDagModifier()
        self.createWindow()

    def tailRigging(self, namePrefix, numOfSpans, ctrllerSize):

        getSelection = cmds.ls(selection=True)
        startJoint = getSelection[0]
        endEffector = getSelection[len(getSelection) - 1]
        ikResult = cmds.ikHandle(sj=startJoint, ee=endEffector, sol='ikSplineSolver', pcv=False, ns=3)
        # [u'ikHandle1', u'effector1', u'curve1']
        # print(ikResult)
        ctrlCurve = ikResult[2]

        cmds.rebuildCurve(ctrlCurve, s=numOfSpans)
        cvCount = cmds.getAttr(ctrlCurve + '.spans') + cmds.getAttr(ctrlCurve + '.degree')
        print (cvCount)
        cvList = []
        for i in range(cvCount):
            cvList.append(ctrlCurve + '.cv[' + str(i) + ']')

        print (cvList)


        cvCount = cmds.getAttr(ctrlCurve + '.spans') + cmds.getAttr(ctrlCurve + '.degree')
        print (cvCount)
        cvList = []
        for i in range(cvCount):
            cvList.append(ctrlCurve + '.cv[' + str(i) + ']')
        print (cvList)

        clusterList = []

        for i in range(len(cvList)):
            newClusterName = namePrefix + 'cluster_' + str(i - 1) + '_'
            if i == 0 or i == 1 or i == len(cvList) - 1:
                pass
            elif i == len(cvList) - 2:
                newCluster = cmds.cluster([cvList[len(cvList) - 1], cvList[len(cvList) - 2]], n=newClusterName)
                clusterList.append(newCluster[1])
            else:
                newCluster = cmds.cluster(cvList[i], n=newClusterName)
                clusterList.append(newCluster[1])
        print(clusterList)
        clusterPosList = []
        ctrllerList = []
        for i in range(len(clusterList)):
            tmpPos = cmds.xform(clusterList[i], q=True, ws=True, piv=True)
            tmpPos = [tmpPos[0], tmpPos[1], tmpPos[2]]
            clusterPosList.append(tmpPos)
            newCtrllerName = namePrefix + 'ctrller_' + str(i + 1)
            newCtrller = cmds.circle(n=newCtrllerName, c=tmpPos, r=ctrllerSize)
            newCtrllerCenter = cmds.objectCenter(newCtrller[0], gl=True)
            cmds.xform(newCtrller, pivots=newCtrllerCenter, ws=True)
            cmds.makeIdentity(newCtrller, apply=True)
            cmds.parentConstraint(newCtrller, clusterList[i])
            ctrllerList.append(newCtrller[0])
        print(clusterPosList)
        print(ctrllerList)
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

        self.namePrefixInput = cmds.textFieldGrp(label='Name Prefix: ', text='name_')
        self.numOfSpansInput = cmds.intSliderGrp(field=True, label='Number of Spans/Controllers: ',
                                        minValue=1, value=4)

        self.ctrllerSizeInput = cmds.floatSliderGrp(field=True, label='Size of Controllers: ',
                                                    value=1.0)
        self.dscActionBtn = cmds.button(label='Apply', command=self.btnAction)

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


















