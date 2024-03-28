import maya.cmds as mc

'''checkbox functions'''






def updateResolution():
    graph = mc.textField(bifrostName, q = True, tx = True)
    resolution = mc.intField(outputSamples, q = True, v = True)
    mc.setAttr(graph + '.outSamples', resolution)
    mc.setAttr(graph + '.HermiteCurveSamples', mc.intField(curveSamples, q=True, v = True))
    









splineCreatorWindowID = "makeSplineWindow"
if mc.window(splineCreatorWindowID, exists=True):
    mc.deleteUI(splineCreatorWindowID)
mc.window(splineCreatorWindowID, t = "MakeSpline")
mc.showWindow(splineCreatorWindowID)


'''Set up main Layout'''
fullLayout = mc.columnLayout()

'''Set up first section layout'''
sectionOneFrame = mc.frameLayout(l = 'Setup Input Objects', w = 400, cll = 0)
sectionOneUIElements = mc.rowColumnLayout(nc=3, parent = sectionOneFrame, cw = [(1,100), (2,200), (3,100)])


'''Set up UI for first section'''

mc.text(l = 'Bifrost Graph')
bifrostName = mc.textField(ed = True)
mc.button(l = '<<<', c = "setGraphToUse(bifrostName)")

mc.text(l = 'Control Objects')
controlObjectListTxt = mc.textField(ed = True)
mc.button(l = '<<<', c = "collectControlObjects(controlObjectListTxt)")


'''Set up spline properties UI'''
propertiesSectionLayout = mc.frameLayout(l = 'Spline Properties', parent = fullLayout)
outputSamplesUI= mc.rowColumnLayout(nc = 2, parent = propertiesSectionLayout, cw = [(1,100), (2,50)])

mc.text(l = "Curve Resolution")
curveSamples = mc.intField(ed=True, w = 50, v = 50)

outputSamplesUI= mc.rowColumnLayout(nc = 4, parent = propertiesSectionLayout, cw = [(1,100), (2,50), (3,150), (4,100)])

mc.text(l = "Output Samples")
outputSamples = mc.intField(ed=True, w = 50, v = 20)
mc.text(' ')
mc.button(l = 'Update', c = 'updateResolution()')


'''Set up execution section Layout'''
executionSectionLayout = mc.frameLayout(l = 'GO!', parent = fullLayout)
executionSectionControls= mc.rowColumnLayout(nc = 5, parent = executionSectionLayout, cw = [(1,75), (2,75), (3,100), (4,50), (5,100)])


'''Set up execution Section UI'''
mc.text('Controllers')
mc.text('-------')
mc.button(l = 'Connect!', c = 'setupRigComponents()')
mc.text('-')
mc.button(l='Disconnect!', c = 'connectControllers(False)')

mc.separator(p = executionSectionLayout)
executionSectionJoints= mc.rowColumnLayout(nc = 1, parent = executionSectionLayout, cw = [(1,400)])



mc.button(l = 'Make Joints!', c = "execution()", p = executionSectionJoints)
mc.button(l = 'Test Feature', c = "testFeature()", p = executionSectionJoints)


def confirm_prompt():
    """Function to display a confirmation dialog."""
    result = mc.confirmDialog(
        title='Confirm',
        message='Would you like to replace the current rig?',
        button=['Yes','No'],
        defaultButton='Yes',
        cancelButton='No',
        dismissString='No')

    if result == 'Yes':
        replaceCurrentRigController()
    else:
        setupOrder()

def replaceCurrentRigController():
    mc.select('HermiteControlRig')
    mc.delete()
    makeControllerObject()

def makeControllerObject():

    rigName = 'HermiteControlRig'
    rigMainControl = mc.circle(n = rigName, r = 5, )
    mc.xform(ro = (90, 0, 0) )
    mc.makeIdentity(a = 1)
    mc.addAttr(rigMainControl, dt="string", ln="order")
    setupOrder()


def setupOrder():
    controlObjectList = mc.textField(controlObjectListTxt, q=True, tx=True).split('|')
    order = [str(i) for i in range(len(controlObjectList))]
    mc.setAttr('HermiteControlRig.order', ",".join(order), type="string")

def createMainController():
    controlObjectList = mc.textField(controlObjectListTxt, q = True, tx = True).split('|')

    #connecting main rig Controller to bfgraph node and adding order attribute
    rigName = 'HermiteControlRig'
    if not mc.objExists(rigName):
        makeControllerObject()
    else:
        mc.warning('Main Controller already exists')
        confirm_prompt()
    return rigName

    

def testFeature():
    for obj in mc.ls(sl=1):
        mc.setAttr(f'{obj}.String_On_Off', edit=True, keyable=True)
    

def setupLocators():
    locators = mc.textField(controlObjectListTxt, q = True, tx = True).split('|')
    for loc in locators:
        print('made it in')
        if not mc.attributeQuery('String_On_Off', node=loc, exists=True):
            print('adding attribute')
            mc.addAttr(loc, at="bool", ln="String_On_Off")
            mc.setAttr(f'{loc}.String_On_Off', True)

#Get the name of the bifrost graph you would like to use
def setGraphToUse(txtField):
    selection = mc.listRelatives(s = True)
    print(selection)
    if len(selection) == 0:
        mc.warning('Please select a bifrost Graph')
    elif len(selection) > 1:
        mc.warning('Please only select 1 bifrost Graph')
    elif mc.objectType(selection) != 'bifrostGraphShape':
        mc.warning('please Select a bifrost Graph')
    else:
        mc.textField(txtField, e = True, tx = selection[0])
    
#Get a list of the objects you would like to use for the curves control objects
def collectControlObjects(ctrlObjects):
    selection = mc.ls(sl = True)
    mc.textField(ctrlObjects, e = True, tx = '|'.join(selection))

def setupRigComponents():
    mainCtrl = createMainController()
    connectControllers(True, mainCtrl)

'''Connect the controller objects to the input of the bifrost graph'''
def connectControllers(connect, ctrlName = None):
    print('connectControllers')
    if mc.textField(bifrostName, q = True, tx = True) == '':
        mc.warning('Please choose a Bifrost Graph')
    elif mc.textField(controlObjectListTxt, q = True, tx = True) == '':
        mc.warning('Please choose the controllers that will drive the spline')
    else:
        controlObjectList = mc.textField(controlObjectListTxt, q = True, tx = True).split('|')
        graph = mc.textField(bifrostName, q = True, tx = True)
        if connect:
            setupLocators()
            
        
        if connect:
            for i in range(len(controlObjectList)):
                print(controlObjectList[i])
                if not mc.isConnected(controlObjectList[i] + '.worldMatrix[0]', graph + '.in_Matrices_one[{0}]'.format(i)):
                    mc.connectAttr(controlObjectList[i] + '.worldMatrix[0]', graph + '.in_Matrices_one[{0}]'.format(i), f=True)
                if not mc.isConnected(controlObjectList[i] + '.String_On_Off', graph + '.AnchorStates[{0}]'.format(i)):
                    mc.connectAttr(controlObjectList[i] + '.String_On_Off', graph + '.AnchorStates[{0}]'.format(i), f=True)
            if not mc.isConnected(f'{ctrlName}.order', f'{graph}.Order'):
                mc.connectAttr(f'{ctrlName}.order', f'{graph}.Order')
            mc.setAttr(graph + '.reset', False)
            mc.setAttr(graph + '.HermiteCurveSamples', mc.intField(curveSamples, q=True, v=True))
            mc.setAttr(graph + '.outSamples', mc.intField(outputSamples, q=True, v=True))
        else:
            for i in range(len(controlObjectList)):
                print(controlObjectList[i])
                mc.disconnectAttr(controlObjectList[i] + '.worldMatrix[0]', graph + '.in_Matrices_one[{0}]'.format(i))
                mc.disconnectAttr(controlObjectList[i] + '.String_On_Off', graph + '.AnchorStates[{0}]'.format(i))

                # Disconnect all connections to the second parameter
                connections = mc.listConnections(f'{graph}.Order', plugs=True, source=True, destination=False)
                print(connections)
                if connections:
                    for connection in connections:
                        mc.disconnectAttr(connection, f'{graph}.Order')

                mc.setAttr(graph + '.reset', True)
    global connected
    connected = True


'''Connect the output objects to the t/r/s of the bifrost graph'''
def connectOutputJoints():

    
    graph = mc.textField(bifrostName, q = True, tx = True)
    samples = mc.intField(outputSamples, q=True, v=True)
    mc.setAttr(graph + '.outSamples', samples)
    
    for i in range(samples):
        joint = mc.createNode('joint', name='bn_spline{0}'.format(i))
        
        mc.connectAttr(graph + '.translate[{0}]'.format(i), joint + '.translate', f=1)
        # mc.connectAttr(graph + '.rotate[{0}]'.format(i), joint + '.rotate', f=1)
        mc.connectAttr(graph + '.scale[{0}]'.format(i), joint + '.scale', f=1)


def execution():
    
    if not connected:
        print('not connected')
        # connectControllers()
    else:
        print(connected)
    connectOutputJoints()

