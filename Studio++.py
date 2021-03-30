import maya.cmds as cmds
import pymel.core as pm
import mtoa.utils as mutils
import mtoa.aovs as aovs
from mtoa.cmds.arnoldRender import arnoldRender

cmds.loadPlugin("mtoa.mll") #Loading this plugin just in case. Because of the fact that it usually unloads itself for no reason

endAnim = 240
m_angle = 0
objectPath = ""
texturePath = None
hdriPath = None
hdriNode = None
fileNode = None
outPath = ""
light = 10
animPresence = False
lights = []
studioLights = []
nameRC = ""
mainLightDist = 0
mainLightHeight = 0
maxSize = 30
fixedX = 0
extension = "png"
AOVPresence = 0
ogMat = []
currMat = None
prevDist = 0
prevX = 0
prevY = 0
prevZ = 0

studioID = 'mainUI'
settingsID = 'settingsUI'
renderID = 'RenderUI'


# UI LAYOUT
#-------------------------------------------------------------------------

# Main Window
mainWindow = cmds.window(title = "Studio++", wh=(500,200), resizeToFitChildren = True)
cmds.rowColumnLayout( numberOfColumns=1)
cmds.showWindow(mainWindow)

cmds.picture( image=r'C:\Documents\maya\2018\prefs\icons\Studio++.jpg' )

cmds.rowColumnLayout(numberOfColumns = 2, columnWidth = [(1, 150), (2, 400)])
pickObjectButton = cmds.button(label="Object file",command="objectPath = pickPath()")
objPathL = cmds.text( label='' )
pickTextureButton = cmds.button(label="Texture file",command="texturePath = pickPath()")
studioButton = cmds.button(label="Studio settings",command="cmds.showWindow(studioWindow)", en=True)
pickPathButton = cmds.button(label="Output Path",command="outPath = pickPathOutput()")
opPathL = cmds.text( label='' )
cmds.rowColumnLayout(numberOfColumns = 3, columnWidth=(1,15))
cmds.text( label='' )
rigCB = cmds.checkBox( label='Is it a rig?', align="right")
cmds.button(label="Help",command="cmds.showWindow(rigWindow)")
cmds.setParent( '..' )
renderButton = cmds.button(label="Render settings",command="cmds.showWindow(renderWindow)", en=True)
processButton = cmds.button(label="Process",command="initialCheck(lightController)", en=False)
cmds.text( label='' )

cmds.text( label='' )
cmds.text( label='' )
renViewB = cmds.button(label="RenderView", en=False, command="cmds.arnoldRenderView()")
startRenB = cmds.button(label="Start Render", en=False, command="startRender()")


# Studio settings
studioWindow = cmds.window(title = "Studio Settings", wh=(400,240), resizeToFitChildren = True, ret=True, menuBar=True)

cmds.menu( label='File', tearOff=True )
cmds.menuItem( label='Open', command="importFile()" )
cmds.menuItem( label='Save', command="save()")

cmds.rowColumnLayout(numberOfColumns = 1)

cmds.text( label='' )
cmds.text( label=' Object', fn="boldLabelFont", align='left' )
rotationController = cmds.floatSliderGrp('rotationSlider', label="Angle", min = -180, max = 180, v = m_angle, field=True, dc='applyRot(cmds.floatSliderGrp(rotationController, q=True, value=True))')
translationController = cmds.floatSliderGrp('translationSlider', label="Move", min = -50, max = 50, v = 0, field=True, dc='applyTrans(cmds.floatSliderGrp(translationController, q=True, value=True))')
cmds.separator()
cmds.text( label='' )
cmds.text( label=' Camera', fn="boldLabelFont", align='left' )
cameraController = cmds.floatSliderGrp('cameraSlider', label="Distance", min = 0.1, max = 10, v = 0.7, field=True, dc='fitCamera(cmds.floatSliderGrp(cameraController, q=True, value=True))')
camFOVController = cmds.floatSliderGrp('camFOVSlider', label="FOV", min = 2.5, max = 3500, v = 35, field=True, dc='fovCamera(cmds.floatSliderGrp(camFOVController, q=True, v=True))')
cmds.separator()
cmds.text( label='' )
cmds.text( label=' Object Lights', fn="boldLabelFont", align='left' )
lightController = cmds.floatSliderGrp('intensObjL', label="Intensity", min = 0, max = 40, v = 10, w = 50, field=True, dc='alterLight(cmds.floatSliderGrp(lightController, q=True, value=True))')
distObjL = cmds.floatSliderGrp('distObjL', label="Distance", min = -50, max = 50, v = 0, field=True, dc='moveLightDist(cmds.floatSliderGrp(distObjL, q=True, value=True))')
xObjL = cmds.floatSliderGrp('xObjL', label="X", min = -50, max = 50, v = 0, field=True, dc='moveLightX(cmds.floatSliderGrp(xObjL, q=True, value=True))')
yObjL = cmds.floatSliderGrp('yObjL', label="Y", min = -50, max = 50, v = 0, field=True, dc='moveLightY(cmds.floatSliderGrp(yObjL, q=True, value=True))')
zObjL = cmds.floatSliderGrp('zObjL', label="Z", min = -50, max = 50, v = 0, field=True, dc='moveLightZ(cmds.floatSliderGrp(zObjL, q=True, value=True))')
scaleObjL = cmds.floatSliderGrp('scaleObjL', label="Scale", min = 0.1, max = 20, v = 1, field=True, dc='scaleLight(cmds.floatSliderGrp(scaleObjL, q=True, value=True))')
cmds.separator()
cmds.text( label='' )
cmds.text( label=' Studio Lights', fn="boldLabelFont", align='left' )
studioLightController = cmds.floatSliderGrp('intensStudL', label="Intensity", min = 0, max = 20, v = 9, field=True, dc='alterStudioLight(cmds.floatSliderGrp(studioLightController, q=True, value=True))')
cmds.separator()
cmds.text( label='' )
matList = cmds.optionMenu( label='     Material', changeCommand="applyMat()" )
cmds.menuItem( label='Original' )
cmds.menuItem( label='Texture' )
cmds.menuItem( label='Clay' )
cmds.menuItem( label='Wireframe' )
cmds.text( label='' )
cmds.rowColumnLayout(numberOfColumns = 3)
cmds.text( label='    ' )
hdriCB = cmds.checkBox( label='HDRI', align="left", onCommand="pickHDRI()", offCommand="noHDRI()")
hdriLabel = cmds.text( label=hdriPath )
cmds.text( label='' )


# Render settings
renderWindow = cmds.window(title = "Render Settings", wh=(510,230), ret=True, menuBar=True)

cmds.menu( label='File', tearOff=True )
cmds.menuItem( label='Open', command="importFile()" )
cmds.menuItem( label='Save', command="save()")

cmds.scrollLayout( 'scrollLayout' )
cmds.columnLayout( adjustableColumn=True )
cmds.frameLayout( label='Sampling', borderStyle='in', en=True, cll=True, cl=True)
cmds.columnLayout()
AAController = cmds.intSliderGrp('AAslider', label="Camera(AA) ", min = 0, max = 10, v = 3, field=True, dc='globRenSet()')
difController = cmds.intSliderGrp('difSlider', label="Diffuse ", min = 0, max = 10, v = 2, field=True, dc='globRenSet()')
specController = cmds.intSliderGrp('specSlider', label="Specular ", min = 0, max = 10, v = 2, field=True, dc='globRenSet()')
tranController = cmds.intSliderGrp('tranSlider', label="Transmission ", min = 0, max = 10, v = 2, field=True, dc='globRenSet()')
SSSController = cmds.intSliderGrp('SSSslider', label="SSS ", min = 0, max = 10, v = 2, field=True, dc='globRenSet()')
volController = cmds.intSliderGrp('volSlider', label="Volume indirect ", min = 0, max = 10, v = 2, field=True, dc='globRenSet()')
cmds.setParent( '..' )
cmds.setParent( '..' )

cmds.frameLayout( label='Ray Depth', borderStyle='in', en=True, cll=True, cl=True)
cmds.columnLayout()
totController = cmds.intSliderGrp('AAslider', label="Total ", min = 0, max = 16, v = 3, field=True, dc='globRenSet()')
difRDController = cmds.intSliderGrp('difSlider', label="Diffuse ", min = 0, max = 16, v = 1, field=True, dc='globRenSet()')
specRDController = cmds.intSliderGrp('specSlider', label="Specular ", min = 0, max = 16, v = 1, field=True, dc='globRenSet()')
tranRDController = cmds.intSliderGrp('tranSlider', label="Transmission ", min = 0, max = 16, v = 8, field=True, dc='globRenSet()')
volRDController = cmds.intSliderGrp('SSSslider', label="Volume ", min = 0, max = 16, v = 0, field=True, dc='globRenSet()')
TDController = cmds.intSliderGrp('volSlider', label="Transparency Depth ", min = 0, max = 16, v = 10, field=True, dc='globRenSet()')
cmds.setParent( '..' )
cmds.setParent( '..' )

cmds.frameLayout( label='AOV', borderStyle='in', en=True, cll=True, cl=True)
cmds.columnLayout()
ZAOV = cmds.checkBox( label='Z-depth', align="right", changeCommand='AOV(ZAOV, "Z")')
difAOV = cmds.checkBox( label='Diffuse', align="right", changeCommand='AOV(difAOV, "diffuse")')
dirAOV = cmds.checkBox( label='Direct', align="right", changeCommand='AOV(dirAOV, "direct")')
indAOV = cmds.checkBox( label='Indirect', align="right", changeCommand='AOV(indAOV, "indirect")')
opAOV = cmds.checkBox( label='Opacity', align="right", changeCommand='AOV(opAOV, "opacity")')
specAOV = cmds.checkBox( label='Specular', align="right", changeCommand='AOV(specAOV, "specular")')
sssAOV = cmds.checkBox( label='SSS', align="right", changeCommand='AOV(sssAOV, "sss")')
shadAOV = cmds.checkBox( label='Shadow', align="right", changeCommand='AOV(shadAOV, "shadow")')
SDAOV = cmds.checkBox( label='Shadow_Diff', align="right", changeCommand='AOV(SDAOV, "shadow_diff")')
SMAOV = cmds.checkBox( label='Shadow_Mask', align="right", changeCommand='AOV(SMAOV, "shadow_mask")')

cmds.setParent( '..' )
cmds.setParent( '..' )

cmds.text( label='' )
cmds.separator()
cmds.text( label='' )

cmds.rowColumnLayout( numberOfColumns=1, columnWidth = (1, 500))
renderName = cmds.textFieldGrp(label="Name", text="Render")
cmds.text( label='' )
cmds.setParent( '..' )

cmds.rowColumnLayout( numberOfColumns=3, columnWidth = (1, 50))
cmds.text( label='' )
cmds.columnLayout()
extMenu = cmds.optionMenu( label='Extension', changeCommand="changeExt()" )
cmds.menuItem( label='png' )
cmds.menuItem( label='exr' )
cmds.menuItem( label='jpeg' )
cmds.menuItem( label='tiff' )
cmds.setParent( '..' )

resolutionValue = cmds.intFieldGrp( numberOfFields=2, label='Resolution', value1=960, value2=540, changeCommand='prevRes()')
cmds.text( label='' )
animation = cmds.checkBox( label='Animation', align="right", changeCommand='applyRot(cmds.floatSliderGrp(rotationController, q=True, value=True))')
animRange = cmds.intFieldGrp( numberOfFields=1, label='Range', value1 = endAnim, en=False, changeCommand='applyRot(cmds.floatSliderGrp(rotationController, q=True, value=True))')
cmds.text( label='' )
rotAnim = cmds.checkBox( label='Rotation', en=False, align="right", changeCommand='applyRot(cmds.floatSliderGrp(rotationController, q=True, value=True))')

# Rig Help window
rigWindow = cmds.window(title = "Rig help", wh=(700,500), resizeToFitChildren = True, ret=True)
cmds.rowColumnLayout( numberOfColumns=1, columnWidth=(1, 700) )
cmds.text( label='' )
cmds.rowColumnLayout( numberOfColumns=2, columnWidth=[(1, 350), (2, 350)] )
cmds.text( label='No rig mode', fn="boldLabelFont" )
cmds.text( label='Rig mode', fn="boldLabelFont" )
cmds.text( label='' )
cmds.text( label='' )
cmds.rowColumnLayout( numberOfColumns=2, columnWidth=[(1, 175), (2, 175)] )
cmds.picture( image=r'C:\Documents\maya\2018\prefs\icons\Rig help 1.jpg' )
cmds.picture( image=r'C:\Documents\maya\2018\prefs\icons\Rig help 2.jpg' )
cmds.setParent( '..' )
cmds.rowColumnLayout( numberOfColumns=2, columnWidth=[(1, 87), (2, 175), (3, 87)] )
cmds.text( label='' )
cmds.picture( image=r'C:\Documents\maya\2018\prefs\icons\Rig help 3.jpg' )
cmds.text( label='' )
cmds.setParent( '..' )
cmds.text( label='There can be only objects or\n the rigged object has only simple joints in its hierarchy.', fn="boldLabelFont" )
cmds.text( label="It's professionally rigged with groups and controls and\n uses 'no transform' to prevent double transformations.", fn="boldLabelFont" )
cmds.text( label='' )
#-------------------------------------------------------------------------


# HDRI
#-------------------------------------------------------------------------

# Get Object's path
def pickPath():
    tempString = cmds.fileDialog2(dialogStyle=1, fm=1)
    if tempString != None:
        cmds.text(objPathL, e=True, label=tempString[0])
        return tempString

# Get Output's path        
def pickPathOutput():
    tempString = cmds.fileDialog2(dialogStyle=1, fm=2)
    if tempString != None:
        cmds.text(opPathL, e=True, label=tempString[0])
        cmds.button(processButton, e=True, en=True)
        return tempString  
        
# The function that makes HDRI for the arealights possible.
def pickHDRI():
    #Needed variables to keep the HDRI existing (For when it's not actually applied)
    global hdriPath
    global hdriNode
    global fileNode
    
    # If there is not an HDRI yet, the user will have to select one.
    if hdriPath == None:
        temp = cmds.fileDialog2(dialogStyle=1, fm=1)
        hdriPath = temp[0]
    
    # If the HDRI already had been selected previously, it will simply use that one.
    if hdriPath != None:
        cmds.text(hdriLabel, e=True, label="     " + hdriPath, en=True)
        
        cmds.setAttr(hdriNode+".fileTextureName", hdriPath, type="string")
        
        for i in lights:
            cmds.connectAttr(fileNode+".outColor", i[0] + ".color")
        for i in studioLights:
            cmds.connectAttr(fileNode+".outColor", i[0] + ".color")
        
# Disconnects the HDRI from the lights and gives the lights their standard color back.
def noHDRI():
    global hdriNode
    
    cmds.text(hdriLabel, e=True, en=False)
    
    for i in lights:
        cmds.disconnectAttr(hdriNode+".outColor", i[0] + ".color")
        cmds.setAttr(i[0] + ".color", 1, 1, 1, type='double3')
    for i in studioLights:
        cmds.disconnectAttr(hdriNode+".outColor", i[0] + ".color")
        cmds.setAttr(i[0] + ".color", 1, 1, 1, type='double3')
#-------------------------------------------------------------------------


# Lights
#-------------------------------------------------------------------------

# To move the lights closer or further
def moveLightDist(lightDist):
    
    # We have to use a "Previous Distance" variable to see how much the lights were moved from the original position.
    # Why? Because the "move" command ADDS translation to the already existing translation. So we will have to move the object
    # first back to the original position to then set it to the distance the user has asked for.
    
    # If all this is needed for the "move" command, why not use "setAttr"? Because the move command has the argument to move
    # the object in their local space, setAttr doesn't.
    global prevDist
    
    for i in lights:
        cmds.move( 0, 0, -prevDist, i[1], os=True, wd=True, r=True)   
        cmds.move( 0, 0, lightDist, i[1], os=True, wd=True, r=True)     
    
    prevDist = lightDist

# To move the lights in X direction
def moveLightX(lightX):
    global prevX
    
    for i in lights:
        cmds.move( -prevX, 0, 0, i[1], r=True, ws=True)
        cmds.move( lightX, 0, 0, i[1], r=True, ws=True)
    
    prevX = lightX

# To move the lights in Y direction
def moveLightY(lightY):
    global prevY
    
    for i in lights:
        cmds.move( 0, -prevY, 0, i[1], r=True, ws=True)   
        cmds.move( 0, lightY, 0, i[1], r=True, ws=True)     
    
    prevY = lightY

# To move the lights in Z direction
def moveLightZ(lightZ):
    global prevZ
    
    for i in lights:
        cmds.move( 0, 0, -prevZ, i[1], r=True, ws=True)   
        cmds.move( 0, 0, lightZ, i[1], r=True, ws=True)     
    
    prevZ = lightZ

# Changing the scale of the lights
def scaleLight(lightScale):
    
    for i in lights:
        cmds.setAttr(i[1] + ".scaleX", lightScale)
        cmds.setAttr(i[1] + ".scaleY", lightScale) 
        cmds.setAttr(i[1] + ".scaleZ", lightScale) 
    
# The function to create the lights for the object.
# With some formulas it will determine the distance, size and light intensity of the lights based on the Bounding box size of the objects combined.
# Honestly, the formula is not 100% which will usually give the end result of overlighting or underlighting. But it should be close.
def createLight(angle, intensity, distance, pivot):
    mainLightDist = (distance * 2) + pivot
    mainLightHeight = distance / 2
    AL = mutils.createLocator('aiAreaLight', asLight=True)
    cmds.move( 0, 0, pivot, AL[1], r=True)
    cmds.setAttr(AL[1]+".rotateY", angle)
    cmds.setAttr(AL[1]+".rotateX", -30)
    cmds.move( 0, 0, mainLightDist, AL[1], os=True, wd=True)
    cmds.move( 0, mainLightHeight, 0, AL[1], r=True)
    cmds.scale(distance,distance,distance, AL[1], absolute=True)
    cmds.setAttr(AL[0]+".intensity", intensity)
    cmds.setAttr(AL[0]+".exposure", (intensity / 2) + 2)
    cmds.aimConstraint( 'Objects', AL, aimVector=(0.0, 0.0, -1.0))
    
    cmds.floatSliderGrp(scaleObjL, e=True, max = distance + 10, v = distance)
    
    lights.append(AL)
    
# The function to create the lights for the whole studio.
def createStudioLight(angle, intensity, distance, pivot):
    AL = mutils.createLocator('aiAreaLight', asLight=True)
    cmds.move( 0, 0, pivot, AL[1], r=True)
    cmds.setAttr(AL[1]+".rotateY", angle)
    cmds.setAttr(AL[1]+".rotateX", -30)
    cmds.move( 0, 0, (distance * 2) + pivot, AL[1], os=True, wd=True)
    cmds.move( 0, distance / 2, 0, AL[1], r=True)
    cmds.scale(distance,distance,distance, AL[1], absolute=True)
    cmds.setAttr(AL[0]+".intensity", intensity * 2)
    cmds.setAttr(AL[0]+".exposure", intensity + 2)
    
    studioLights.append(AL)

# The code to change the intensity and exposure of the lights
def alterLight(light):
    for i in lights:
        cmds.setAttr(i[1]+".intensity", light)
        cmds.setAttr(i[1]+".exposure", (light / 2) + 2)

def alterStudioLight(light):
    for i in studioLights:
        cmds.setAttr(i[1]+".intensity", light * 2)
        cmds.setAttr(i[1]+".exposure", light + 2)

#-------------------------------------------------------------------------


# MATERIALS
#-------------------------------------------------------------------------

#Function that takes care of applying a chosen texture or not.
def applyMat():
    
    # The chosen texture path that was chosen.
    global texturePath
    # The Original material that came with the imported object.
    global ogMat
    # The needed variable to see if there is a material applied and if we should delete it or not.
    global currMat
    
    # Saving all original materials that came with the object into a variable
    # in case the user wants to use it again after applying another material.
    mats = cmds.ls(mat=True)
    
    # Gets rid of the current material to make the applying much easier.
    if currMat != None:
        cmds.delete(currMat)
    
    # Checking which material the user selected in the UI.
    matType = cmds.optionMenu(matList, q=True, value=True)
    
    # Original material
    if matType == "Original":
        currMat = None
        objs = cmds.ls(type='mesh')
        for i in objs:
            cmds.select(i)
            for j in ogMat:
                if i == j[0]:
                    cmds.hyperShade( assign=j[1])
    
    # Texture material
    if matType == "Texture":
        aiMat = cmds.shadingNode('aiStandardSurface', asShader=True)
        cmds.setAttr(aiMat + ".specular", 0)
        if texturePath != None:
            # Sending the texturemap and material node to apply it on to a function
            textureDiffuse(texturePath, aiMat)  
        
        cmds.select( 'Objects' )
        cmds.hyperShade( assign=aiMat)
        currMat = aiMat
    
    # Clay material
    if matType == "Clay":
        aiMat = cmds.shadingNode('aiStandardSurface', asShader=True)
        cmds.setAttr(aiMat + ".specular", 0)
        cmds.select( 'Objects' )
        cmds.hyperShade( assign=aiMat)
        currMat = aiMat
    
    # Wireframe material
    if matType == "Wireframe":
        aiWF = cmds.shadingNode('aiWireframe', asShader=True)
        cmds.select( 'Objects' )
        cmds.hyperShade( assign=aiWF)
        currMat = aiWF
    
# Creating a file node to put the texturemap in and then connecting that file node to the given material node.
def textureDiffuse(textureMap, aiMaterial):
    cmds.setAttr(aiMaterial + ".base", 1)
    fileNode = cmds.createNode('file')
    cmds.setAttr(fileNode+".fileTextureName", textureMap[0], type="string")
    cmds.connectAttr(fileNode+".outColor", aiMaterial + ".baseColor")
#-------------------------------------------------------------------------


# OBJECT
#-------------------------------------------------------------------------

# Simply rotates the object.
def rotObject(angle):
    cmds.setAttr("Objects.rotateY", angle)

# Gives the rotation animation to the object.
# An angle is given with it in case the user rotated the object, which we obviously want to start to rotate from and end the rotation at.
def giveAnim(angle):
    # Removes all keys in the object just to be sure the object has no animations anymore.
    cmds.cutKey('Objects', cl=True)
    
    # Gets the range from the UI to see what the duration is of our animation.
    range = int(cmds.intFieldGrp (animRange, q = True, v1=True))  
      
    cmds.currentTime(0)
    cmds.playbackOptions( minTime='0sec', maxTime=range )
    
    # Placing the keys
    cmds.setKeyframe( 'Objects', t=[0], at='ry', v=angle )
    cmds.setKeyframe( 'Objects', t=[range], at='ry', v=360 + angle )
    
    # Setting the animation curves in the graph editor to linear so the user gets a seamless rotation loop
    cmds.keyTangent( 'Objects', itt='linear', ott='linear')

# All the rotation functions and animation functions are combined here. Calculations to apply them or not are done here.
def applyRot(rotation):
    
    # Querying the information from the UI
    animPresence = cmds.checkBox(animation, query=True, value=True)
    rotPresence = cmds.checkBox(rotAnim, query=True, value=True)
    
    # Applying rotation to the object, no other fancy checking code needed.
    rotObject(rotation)
    
    # Changing the UI based on input
    if animPresence == True:
        cmds.intFieldGrp( animRange, e=True, en=True)
        cmds.checkBox( rotAnim, e=True, en=True)
        
        # Rotation was asked for? It will be applied. Otherwise, all keys will be deleted to make sure.
        if rotPresence == True:
            giveAnim(rotation)
        else:
            cmds.cutKey('Objects', cl=True)
            
    # Changing the UI based on input 
    else:
        cmds.intFieldGrp( animRange, e=True, en=False)
        cmds.checkBox( rotAnim, e=True, en=False)
        
# Moves the object in X direction
def applyTrans(translation):
    cmds.setAttr("Objects.translateX", fixedX + translation)
#-------------------------------------------------------------------------

# Camera
#-------------------------------------------------------------------------

# Sets the distance of the camera. It doesn't use the setAttr or move command as there is a "viewFit" command. 
# ViewFit move the camera until it can see all the objects. The f- argument (focus) can be seen as the "Tolerance" of this function.
# The variable nameRC stands for "name Render Camera", so a camera is given, the objects it's to aim for and the amount of focus.
# The focus only works from 0 to 1, so if the user wants to zoom in more, we will have to take it over when the value goes over 1.
def fitCamera(distance):
    
    if distance <= 1.0:
        cmds.viewFit(nameRC , 'Objects', f=distance)
    else:
        cmds.viewFit(nameRC , 'Objects')
        currentZ = cmds.getAttr(nameRC + ".translateZ")
        cmds.setAttr( nameRC + ".translateZ", currentZ / distance)

# Changed the Focal length of the camera. (This was requested by another student when trying out the script.)
def fovCamera(FOV):
    cmds.setAttr(nameRC + ".focalLength", FOV)
    
#-------------------------------------------------------------------------


# MAIN 
# calculations and calling of the functions.
#-------------------------------------------------------------------------


def initialCheck(lightController):
    
    # Checking if the user let us know it's a rig or not through the UI.
    rig = cmds.checkBox(rigCB, query=True, value=True)
    
    # This IF statement has become OBSOLETE. But left it in here as a second check
    # in case the UI still let the user click on the process button without having selected an output path.
    if outPath != "":
        
        # Loading the information from the interface
        if objectPath != "":
            nodes = cmds.file(objectPath, i=True)

        light = cmds.floatSliderGrp(lightController, q=True, value=True)
        animPresence = cmds.checkBox(animation, query=True, value=True)
        
        # Grouping objects based on if it's a rig or not.
        # "Why not do it as if it's always a rig?"
        # There are also rigs that are too simple and don't have the "noTransform" group which will end up in DOUBLE TRANSFORMS,
        # Which is bad for the rotation animation.
        try:
            if rig == False:
                allPolys = cmds.ls(type='mesh') 
                cmds.group(allPolys, n='Objects')
            else:
                cmds.select(all=True)
                cmds.group(n='Objects')
            
            # Starts the main process
            Process(lightController)
                                                                             
        except:
            cmds.error("No valid objects present in scene or imported.")
            
        #Process(lightController) # THIS POSITION IS FOR THE PURPOSE OF DEBUGGING
    else:
        # This error will be shown if the output path was not selected.
        # EDIT: THIS HAS BECOME OBSOLETE. As the UI now can change based on user input.
        # Now the user can only process when the output path was selected.
        cmds.error("Please select an output path for the renders and scene file.")

 
        
    	
def Process(lightController):
    
    # Changing the process button to a reset button to give the chance to reset when there is an error.
    # The user cannot process anymore anyway when the process is already done. Once a process is done, a reset is needed.
    cmds.button( processButton, e = True, label="Reset", command="reset()")
    
    # Collecting the original material of the imported object
    #-------------------------------------------------------------------------
    global ogMat
    
    # Selecting all mesh as they are the only ones capable of holding a material.
    # And of course going through every object to collect the material.
    
    objects = cmds.ls(type="mesh")
    
    # This process is not easily explained. 
    # I've set some print commands to show you how the end results look after almost every line of code.
    
    for i in objects:
        
        shader = cmds.listConnections(i, type="shadingEngine")
        print shader
        
        if shader != None:
            for j in shader:
                linkedMats = cmds.listConnections(shader[0])
                print linkedMats[0]
            
            print "--> " + i
            print "--> " + linkedMats[0]
            print "-----"
            tempLink = [i, linkedMats[0]]
            ogMat.append(tempLink)
        
    print ogMat
    print cmds.ls(type='mesh')
    #-------------------------------------------------------------------------
    
    # Getting the size of the object(s) by asking for the Bounding Box.
    bbox = cmds.exactWorldBoundingBox('Objects', ii = True)
    
    # If the object is too big, it will be downscaled. If the object is in the air, it will be taken into account
    sizeY = bbox[4] - bbox[1]
    adjustScale = maxSize / sizeY
    oldY = bbox[1] * adjustScale
    if(sizeY > maxSize):        
        cmds.scale(adjustScale, adjustScale, adjustScale, 'Objects', absolute=True)
        bbox = cmds.exactWorldBoundingBox('Objects', ii = True)
        cmds.setAttr('Objects.translateY', -(bbox[1] - oldY) )
    
    # If the object goes through the floor, this fixes it.
    bbox = cmds.exactWorldBoundingBox('Objects', ii = True)
    if bbox[1] < 0:
        oldY = cmds.getAttr("Objects"+".translateY")
        cmds.setAttr("Objects"+".translateY", oldY + (-bbox[1]))
    
    # Centering the group of objects.
    offX = cmds.objectCenter('Objects',x=True)
    offZ = cmds.objectCenter('Objects',z=True)
    cmds.setAttr("Objects"+".translateX", -offX)
    cmds.setAttr("Objects"+".translateZ", -offZ)
    fixedX = -offX
    
    # Afterwards, new boundingbox values are given so we have the current fixed object's values
    bbox = cmds.exactWorldBoundingBox('Objects', ii = True)
    sizeX = bbox[3] - bbox[0]
    sizeY = bbox[4] - bbox[1]
    sizeZ = bbox[5] - bbox[2]
    
    #Creation of the studio
    #BG Screen
    studioBG = cmds.polyPlane( sx=10, sy=10, w=sizeX * 100, h=sizeY * 10 * 2)
    currentPos = -sizeY * 2
    cmds.setAttr(studioBG[0]+".translateZ", currentPos)
    cmds.setAttr(studioBG[0]+".displaySmoothMesh", 2)
    bboxBG = cmds.exactWorldBoundingBox(studioBG[0])
    
    # We use the bend tool to get the nice curve in our screen.
    bendTool = cmds.nonLinear( type='bend', highBound = 0, curvature=90)
    
    cmds.setAttr(bendTool[1]+".scaleX", sizeY / 2)
    cmds.setAttr(bendTool[1]+".scaleY", sizeY / 2)
    cmds.setAttr(bendTool[1]+".scaleZ", sizeY / 2)
    cmds.setAttr(bendTool[1]+".rotateX", 90)
    cmds.setAttr(bendTool[1]+".rotateZ", 90)
    cmds.setAttr(bendTool[1]+".translateZ", currentPos)
    
    # Setting the distance of the BG screen based on which side of the object is the widest.
    if sizeX > sizeZ:
        cmds.setAttr(studioBG[0]+".translateZ", currentPos - (sizeX / 3))
        cmds.setAttr(bendTool[1]+".translateZ", currentPos - (sizeX / 3))
    else:
        cmds.setAttr(studioBG[0]+".translateZ", currentPos - (sizeZ / 3))
        cmds.setAttr(bendTool[1]+".translateZ", currentPos - (sizeZ / 3))       
    
    # Camera
    renderCamera = cmds.camera()
    global nameRC
    nameRC = renderCamera[0]
    cmds.setAttr(nameRC+".translateY", sizeY / 2)
    fitCamera(cmds.floatSliderGrp(cameraController, q=True, value=True))
    
    # Lights
    createLight(-45, light, sizeY, 0)
    createLight(45, light, sizeY, 0)
    createStudioLight(0, light - 1, sizeY * 2, sizeY / 2)
    createStudioLight(0, light - 1, sizeY * 2, sizeY / 2)    
    
    # Creating the needed nodes for the HDRI later.
    global hdriNode
    global fileNode
    fileNode = cmds.createNode('file')
    hdriNode = fileNode
    
    # Changing position of the background light
    z = cmds.getAttr(bendTool[1]+".translateZ") / 2
    cmds.setAttr("aiAreaLight4.translateZ", z)
    currentScale = cmds.getAttr("aiAreaLight4.scaleX")
    cmds.scale(currentScale * 2,currentScale,currentScale, 'aiAreaLight4' , absolute=True)
    cmds.aimConstraint( bendTool[1], 'aiAreaLight4', aim = (0.0, 0.0, -1.0) )
    
    # Running this function to set things up already. Because there is obviously no rotation input yet.          
    applyRot(cmds.floatSliderGrp(rotationController, q=True, value=True))
    
    # Checking if a Texturemap was given before the process button was clicked.
    # If so, the material selector in the UI is set to "Texture" and the Apply material function is being run.
    if texturePath != None:
        cmds.optionMenu(matList, e=True, value="Texture")
        applyMat()
    
    # Saving the scene in a maya file.
    render_file = outPath[0] + "\\scene.mb"
    cmds.file(rename=render_file)
    cmds.file(force=True, save=True, type='mayaBinary')
    
    # Telling the script the process is completed.
    cmds.button(renderButton, e=True, en=True)
    cmds.button(studioButton, e=True, en=True)
    cmds.button(renViewB, e=True, en=True)
    cmds.button(startRenB, e=True, en=True)

# RENDER
#-------------------------------------------------------------------------

# Changing the extension for rendering
def changeExt():
    global extension
    extension = cmds.optionMenu(extMenu, q=True, value=True)

# Setting the resolution
def prevRes():
    cmds.setAttr("defaultResolution.width", int(cmds.intFieldGrp (resolutionValue, q = True, v1=True)))
    cmds.setAttr ("defaultResolution.height", int(cmds.intFieldGrp (resolutionValue, q = True, v2=True)))

# Setting all Arnold Render settings
def globRenSet():
    cmds.setAttr('defaultArnoldRenderOptions.AASamples', cmds.intSliderGrp(AAController, q=True, v=True))
    cmds.setAttr('defaultArnoldRenderOptions.GIDiffuseSamples', cmds.intSliderGrp(difController, q=True, v=True))    
    cmds.setAttr('defaultArnoldRenderOptions.GISpecularSamples', cmds.intSliderGrp(specController, q=True, v=True))
    cmds.setAttr('defaultArnoldRenderOptions.GITransmissionSamples', cmds.intSliderGrp(tranController, q=True, v=True))
    cmds.setAttr('defaultArnoldRenderOptions.GISssSamples', cmds.intSliderGrp(SSSController, q=True, v=True))
    cmds.setAttr('defaultArnoldRenderOptions.GIVolumeSamples', cmds.intSliderGrp(volController, q=True, v=True))
    
    cmds.setAttr('defaultArnoldRenderOptions.GITotalDepth', cmds.intSliderGrp(totController, q=True, v=True))
    cmds.setAttr('defaultArnoldRenderOptions.GIDiffuseDepth', cmds.intSliderGrp(difRDController, q=True, v=True))
    cmds.setAttr('defaultArnoldRenderOptions.GISpecularDepth', cmds.intSliderGrp(specRDController, q=True, v=True))
    cmds.setAttr('defaultArnoldRenderOptions.GITransmissionDepth', cmds.intSliderGrp(tranRDController, q=True, v=True))
    cmds.setAttr('defaultArnoldRenderOptions.GIVolumeDepth', cmds.intSliderGrp(volRDController, q=True, v=True))
    cmds.setAttr('defaultArnoldRenderOptions.autoTransparencyDepth', cmds.intSliderGrp(TDController, q=True, v=True))

# Setting AOV's whenever a checkbox is checked or unchecked.
def AOV(CB, passName):
    global AOVPresence
    
    AOVbool = cmds.checkBox(CB, query=True, value=True)
    if AOVbool == True:
        aovs.AOVInterface().addAOV(passName)
        AOVPresence += 1
    else:
        aovs.AOVInterface().removeAOV(passName)
        AOVPresence -= 1


# Here is the rendering done.
def startRender():
    global extension
    
    # Querying all the data from the UI.
    nameRenderFile = cmds.textFieldGrp(renderName, q=True, text=True)    
    animPresence = cmds.checkBox(animation, query=True, value=True)
    resWidth = int(cmds.intFieldGrp (resolutionValue, q = True, v1=True))
    resHeight = int(cmds.intFieldGrp (resolutionValue, q = True, v2=True))
     
    # Here all the needed render specific render settings are set and then the render will be started.
    # If there is no animation present, then a single frame is rendered.
    if animPresence == False:
        cmds.currentTime(0)
        cmds.createNode('aiAOVDriver', n='defaultArnoldDriver')
        cmds.setAttr('defaultArnoldDriver.colorManagement', 1)
        cmds.setAttr("defaultArnoldDriver.ai_translator", extension, type="string")
        cmds.setAttr("defaultArnoldDriver.pre",  outPath[0] + "\\" + nameRenderFile + "-<RenderPass>", type="string")
        
        arnoldRender(resWidth, resHeight, True, True,nameRC, ' -layer defaultRenderLayer')
        
    else:
        # If there is an animation present, a render sequence will be made instead of a single frame.
        applyRot(cmds.floatSliderGrp(rotationController, q=True, value=True))
        now = cmds.currentTime(q=True)
        
        cmds.createNode('aiAOVDriver', n='defaultArnoldDriver')
        cmds.setAttr('defaultArnoldDriver.colorManagement', 1)
        cmds.setAttr("defaultArnoldDriver.ai_translator", extension, type="string")
        
        # The render sequence function creates watermarks on the render without a license.
        # So I made my own render sequence code. It renders just like it's a single frame,
        # And when it's done, the current time will be set to the next frame and another render is started.
        for x in xrange(0, range):
            cmds.currentTime(x)
            path = outPath[0] + "\\<RenderPass>\\" + nameRenderFile + str(x)
            cmds.setAttr("defaultArnoldDriver.pre", path, type="string")
            arnoldRender(resWidth, resHeight, True, True,nameRC, ' -layer defaultRenderLayer')
        cmds.currentTime(now)
#-------------------------------------------------------------------------


# SAVING SETTINGS TO FILE
# Unfortunately this still requires the user to first create a text file him/herself.
#-------------------------------------------------------------------------
def save():    
    pathTxtFile = cmds.fileDialog2(dialogStyle=1, fm=1)
    fileHandle = open(pathTxtFile[0],'a')  
    
    #Studio settings data
    
    fileHandle.write("obj angle : " + str(cmds.floatSliderGrp(rotationController, q=True, value=True)) + os.linesep)
    fileHandle.write("obj translation : " + str(cmds.floatSliderGrp(translationController, q=True, value=True)) + os.linesep)
    
    fileHandle.write("camera Distance : " + str(cmds.floatSliderGrp(cameraController, q=True, value=True)) + os.linesep)
    fileHandle.write("camera FOV : " + str(cmds.floatSliderGrp(camFOVController, q=True, value=True)) + os.linesep)
    
    fileHandle.write("object light intensity : " + str(cmds.floatSliderGrp(lightController, q=True, value=True)) + os.linesep)
    fileHandle.write("object light distance : " + str(cmds.floatSliderGrp(distObjL, q=True, value=True)) + os.linesep)
    fileHandle.write("object light x : " + str(cmds.floatSliderGrp(xObjL, q=True, value=True)) + os.linesep)
    fileHandle.write("object light y : " + str(cmds.floatSliderGrp(yObjL, q=True, value=True)) + os.linesep)
    fileHandle.write("object light z : " + str(cmds.floatSliderGrp(zObjL, q=True, value=True)) + os.linesep)
    fileHandle.write("object light scale : " + str(cmds.floatSliderGrp(scaleObjL, q=True, value=True)) + os.linesep)
    
    fileHandle.write("studio light intensity : " + str(cmds.floatSliderGrp(studioLightController, q=True, value=True)) + os.linesep)
    
    fileHandle.write("MaterialMode : " + str(cmds.optionMenu(matList, q=True, value=True)) + os.linesep)
    
    fileHandle.write("HDRI presence : " + str(cmds.checkBox(hdriCB, query=True, value=True)) + os.linesep)
    fileHandle.write("HDRI path : " + str(hdriPath) + os.linesep)
        
    #Render settings data
    
    fileHandle.write("Camera AA : " + str(cmds.intSliderGrp(AAController, q=True, v=True)) + os.linesep)
    fileHandle.write("Diffuse : " + str(cmds.intSliderGrp(difController, q=True, v=True)) + os.linesep)
    fileHandle.write("Specular : " + str(cmds.intSliderGrp(specController, q=True, v=True)) + os.linesep)
    fileHandle.write("Transmission : " + str(cmds.intSliderGrp(tranController, q=True, v=True)) + os.linesep)
    fileHandle.write("SSS : " + str(cmds.intSliderGrp(SSSController, q=True, v=True)) + os.linesep)
    fileHandle.write("Volume Indirect : " + str(cmds.intSliderGrp(volController, q=True, v=True)) + os.linesep)
    
    fileHandle.write("RD Total : " + str(cmds.intSliderGrp(totController, q=True, v=True)) + os.linesep)
    fileHandle.write("RD Diffuse : " + str(cmds.intSliderGrp(difRDController, q=True, v=True)) + os.linesep)
    fileHandle.write("RD Specular : " + str(cmds.intSliderGrp(specRDController, q=True, v=True)) + os.linesep)
    fileHandle.write("RD Transmission : " + str(cmds.intSliderGrp(tranRDController, q=True, v=True)) + os.linesep)
    fileHandle.write("RD Volume : " + str(cmds.intSliderGrp(volRDController, q=True, v=True)) + os.linesep)
    fileHandle.write("Transparency Depth : " + str(cmds.intSliderGrp(TDController, q=True, v=True)) + os.linesep)
    
    fileHandle.write("Z-depth AOV : " + str(cmds.checkBox(ZAOV, query=True, value=True)) + os.linesep)
    fileHandle.write("Diffuse AOV : " + str(cmds.checkBox(difAOV, query=True, value=True)) + os.linesep)
    fileHandle.write("Direct AOV : " + str(cmds.checkBox(dirAOV, query=True, value=True)) + os.linesep)
    fileHandle.write("Indirect AOV : " + str(cmds.checkBox(indAOV, query=True, value=True)) + os.linesep)
    fileHandle.write("Opacity AOV : " + str(cmds.checkBox(opAOV, query=True, value=True)) + os.linesep)
    fileHandle.write("Specular AOV : " + str(cmds.checkBox(specAOV, query=True, value=True)) + os.linesep)
    fileHandle.write("SSS AOV : " + str(cmds.checkBox(sssAOV, query=True, value=True)) + os.linesep)
    fileHandle.write("Shadow AOV : " + str(cmds.checkBox(shadAOV, query=True, value=True)) + os.linesep)
    fileHandle.write("Shadow Diffuse AOV : " + str(cmds.checkBox(SDAOV, query=True, value=True)) + os.linesep)
    fileHandle.write("Shadow Mask AOV : " + str(cmds.checkBox(SMAOV, query=True, value=True)) + os.linesep)
    
    fileHandle.write("Extension : " + str(cmds.optionMenu(extMenu, q=True, value=True)) + os.linesep)
    fileHandle.write("Width : " + str(cmds.intFieldGrp (resolutionValue, q = True, v1=True)) + os.linesep)
    fileHandle.write("Height : " + str(cmds.intFieldGrp (resolutionValue, q = True, v2=True)) + os.linesep)
    
    fileHandle.write("Animation Presence : " + str(cmds.checkBox(animation, query=True, value=True)) + os.linesep)
    fileHandle.write("WAnimation Range : " + str(cmds.intFieldGrp (animRange, q = True, v1=True)) + os.linesep)
    fileHandle.write("Rotation Requested : " + str(cmds.checkBox(rotAnim, query=True, value=True)))
    
    fileHandle.close()
#-------------------------------------------------------------------------


# A quick String to Boolean converter as it's needed when reading the save file.
# Putting the string "True" or "False" into a boolean variable doesn't work.
def strToBool(input):
    tempBool = False
    
    if input.strip() == "True":
        tempBool = True
        return tempBool
    else:
        return tempBool


# IMPORTING THE SAVED FILE
#-------------------------------------------------------------------------
def importFile():    
    pathTxtFile = cmds.fileDialog2(dialogStyle=1, fm=1)
    fileHandle = open(pathTxtFile[0],'r')
    
    variables = []
    
    my_str = fileHandle.read()
    settings = my_str.split("\n")
    
    for i in settings:
        temp = i.split(" : ")
        variables.append(temp[1])
    
    #Studio settings data
    
    cmds.floatSliderGrp(rotationController, e=True, value=float(variables[0]))
    cmds.floatSliderGrp(translationController, e=True, value=float(variables[1]))
    
    cmds.floatSliderGrp(cameraController, e=True, value=float(variables[2]))
    cmds.floatSliderGrp(camFOVController, e=True, value=float(variables[3]))
    
    cmds.floatSliderGrp(lightController, e=True, value=float(variables[4]))
    cmds.floatSliderGrp(distObjL, e=True, value=float(variables[5]))
    cmds.floatSliderGrp(xObjL, e=True, value=float(variables[6]))
    cmds.floatSliderGrp(yObjL, e=True, value=float(variables[7]))
    cmds.floatSliderGrp(zObjL, e=True, value=float(variables[8]))
    cmds.floatSliderGrp(scaleObjL, e=True, value=float(variables[9]))
    
    cmds.floatSliderGrp(studioLightController, e=True, value=float(variables[10]))
    
    cmds.optionMenu(matList, e=True, value=variables[11].strip())   
    cmds.checkBox(hdriCB, e=True, value=strToBool(variables[12]))
    
    global hdriPath
    hdriPath = variables[13]
        
    #Render settings data
    cmds.intSliderGrp(AAController, e=True, value=int(variables[14]))
    cmds.intSliderGrp(difController, e=True, value=int(variables[15]))
    cmds.intSliderGrp(specController, e=True, value=int(variables[16]))
    cmds.intSliderGrp(tranController, e=True, value=int(variables[17]))
    cmds.intSliderGrp(SSSController, e=True, value=int(variables[18]))
    cmds.intSliderGrp(volController, e=True, value=int(variables[19]))
    
    cmds.intSliderGrp(totController, e=True, value=int(variables[20]))
    cmds.intSliderGrp(difRDController, e=True, value=int(variables[21]))
    cmds.intSliderGrp(specRDController, e=True, value=int(variables[22]))
    cmds.intSliderGrp(tranRDController, e=True, value=int(variables[23]))
    cmds.intSliderGrp(volRDController, e=True, value=int(variables[24]))
    cmds.intSliderGrp(TDController, e=True, value=int(variables[25]))
    
    cmds.checkBox(ZAOV, e=True, value=strToBool(variables[26]))
    cmds.checkBox(difAOV, e=True, value=strToBool(variables[27]))
    cmds.checkBox(dirAOV, e=True, value=strToBool(variables[28]))
    cmds.checkBox(indAOV, e=True, value=strToBool(variables[29]))
    cmds.checkBox(opAOV, e=True, value=strToBool(variables[30]))
    cmds.checkBox(specAOV, e=True, value=strToBool(variables[31]))
    cmds.checkBox(sssAOV, e=True, value=strToBool(variables[32]))
    cmds.checkBox(shadAOV, e=True, value=strToBool(variables[33]))
    cmds.checkBox(SDAOV, e=True, value=strToBool(variables[34]))
    cmds.checkBox(SMAOV, e=True, value=strToBool(variables[35]))
    
    cmds.optionMenu(extMenu, e=True, value=variables[36].strip())
    cmds.intFieldGrp(resolutionValue, e=True, value1=int(variables[37]))
    cmds.intFieldGrp(resolutionValue, e=True, value2=int(variables[38]))
    
    cmds.checkBox(animation, e=True, value=strToBool(variables[39]))
    cmds.intFieldGrp(animRange, e=True, value1=int(variables[40]))
    cmds.checkBox(rotAnim, e=True, value=strToBool(variables[41]))
        
    fileHandle.close()
    
    #After collecting the data and putting them in the user interface, all functions have to be triggered to actually apply the changes
    interfaceCommands()
    
# To apply all functions existing in the UI.
def interfaceCommands():
    applyRot(cmds.floatSliderGrp(rotationController, q=True, value=True))
    applyTrans(cmds.floatSliderGrp(translationController, q=True, value=True))
    
    fitCamera(cmds.floatSliderGrp(cameraController, q=True, value=True), cmds.floatSliderGrp(camFOVController, q=True, v=True))
    
    alterLight(cmds.floatSliderGrp(lightController, q=True, value=True))
    moveLightDist(cmds.floatSliderGrp(distObjL, q=True, value=True))
    moveLightX(cmds.floatSliderGrp(xObjL, q=True, value=True))
    moveLightY(cmds.floatSliderGrp(yObjL, q=True, value=True))
    moveLightZ(cmds.floatSliderGrp(zObjL, q=True, value=True))
    scaleLight(cmds.floatSliderGrp(scaleObjL, q=True, value=True))
    
    alterStudioLight(cmds.floatSliderGrp(studioLightController, q=True, value=True))
    
    applyMat()
    
    if cmds.checkBox(hdriCB, q=True, v=True) == True:
        pickHDRI()
    
    #Render settings
    
    globRenSet()
    
    AOV(ZAOV, "Z")
    AOV(difAOV, "diffuse")
    AOV(dirAOV, "direct")
    AOV(indAOV, "indirect")
    AOV(opAOV, "opacity")
    AOV(specAOV, "specular")
    AOV(sssAOV, "sss")
    AOV(shadAOV, "shadow")
    AOV(SDAOV, "shadow_diff")
    AOV(SMAOV, "shadow_mask")
    
    changeExt()
    
    prevRes()
#-------------------------------------------------------------------------


# RESET
#-------------------------------------------------------------------------
   
def reset():
    global texturePath
    texturePath = None
    global lights
    lights = []
    global studioLights
    studioLights = []
    global m_angle
    m_angle = 0
    global endAnim
    endAnim = 240
    global objectPath
    objectPath = ""
    global hdriPath
    hdriPath = None
    global hdriNode
    hdriNode = None
    global fileNode
    fileNode = None
    global outPath
    outPath = ""
    global light
    light = 10
    global animPresence
    animPresence = False
    global nameRC
    nameRC = ""
    global mainLightDist
    mainLightDist = 0
    global mainLightHeight
    mainLightHeight = 0
    global maxSize
    maxSize = 30
    global fixedX
    fixedX = 0
    global extension
    extension = "png"
    global AOVPresence
    AOVPresence = 0
    global ogMat
    ogMat = []
    global currMat
    currMat = None
    global prevDist
    prevDist = 0
    global prevX
    prevX = 0
    global prevY
    prevY = 0
    global prevZ
    prevZ = 0
    
    cmds.floatSliderGrp(rotationController, e=True, value=m_angle)
    cmds.floatSliderGrp(translationController, e=True, value=0)
    
    cmds.floatSliderGrp(cameraController, e=True, value=0.7)
    cmds.floatSliderGrp(camFOVController, e=True, value=35)
    
    cmds.floatSliderGrp(lightController, e=True, value=10)
    cmds.floatSliderGrp(distObjL, e=True, value=0)
    cmds.floatSliderGrp(xObjL, e=True, value=0)
    cmds.floatSliderGrp(yObjL, e=True, value=0)
    cmds.floatSliderGrp(zObjL, e=True, value=0)
    cmds.floatSliderGrp(scaleObjL, e=True, value=1)
    
    cmds.floatSliderGrp(studioLightController, e=True, value=9)
    
    cmds.optionMenu(matList, e=True, value='Original')   
    cmds.checkBox(hdriCB, e=True, value=False)
    
    global hdriPath
    hdriPath = None
        
    #Render settings data
    cmds.intSliderGrp(AAController, e=True, value=3)
    cmds.intSliderGrp(difController, e=True, value=2)
    cmds.intSliderGrp(specController, e=True, value=2)
    cmds.intSliderGrp(tranController, e=True, value=2)
    cmds.intSliderGrp(SSSController, e=True, value=2)
    cmds.intSliderGrp(volController, e=True, value=2)
    
    cmds.intSliderGrp(totController, e=True, value=3)
    cmds.intSliderGrp(difRDController, e=True, value=1)
    cmds.intSliderGrp(specRDController, e=True, value=1)
    cmds.intSliderGrp(tranRDController, e=True, value=8)
    cmds.intSliderGrp(volRDController, e=True, value=0)
    cmds.intSliderGrp(TDController, e=True, value=10)
    
    cmds.checkBox(ZAOV, e=True, value=False)
    cmds.checkBox(difAOV, e=True, value=False)
    cmds.checkBox(dirAOV, e=True, value=False)
    cmds.checkBox(indAOV, e=True, value=False)
    cmds.checkBox(opAOV, e=True, value=False)
    cmds.checkBox(specAOV, e=True, value=False)
    cmds.checkBox(sssAOV, e=True, value=False)
    cmds.checkBox(shadAOV, e=True, value=False)
    cmds.checkBox(SDAOV, e=True, value=False)
    cmds.checkBox(SMAOV, e=True, value=False)
    
    cmds.optionMenu(extMenu, e=True, value='png')
    cmds.intFieldGrp(resolutionValue, e=True, value1=960)
    cmds.intFieldGrp(resolutionValue, e=True, value2=540)
    
    cmds.checkBox(animation, e=True, value=False)
    cmds.intFieldGrp(animRange, e=True, value1=240)
    cmds.checkBox(rotAnim, e=True, value=False)
    
    cmds.button(studioButton, e=True, en=False)
    cmds.button(renderButton, e=True, en=False)
    cmds.button(processButton, e=True, en=False)
    cmds.button(renViewB, e=True, en=False)
    cmds.button(startRenB, e=True, en=False)
    
    cmds.text(objPathL, e=True, label='' )
    cmds.text(opPathL, e=True, label='' )
    cmds.text(hdriLabel, e=True, label='' )    
    
    cmds.intFieldGrp( animRange, e=True, en=False)
    cmds.checkBox( rotAnim, q=True, en=False)
    
    cmds.button( processButton, e = True, label="Process", command="initialCheck(lightController)")
#-------------------------------------------------------------------------