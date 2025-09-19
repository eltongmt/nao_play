import numpy as np

FRAME_TORSO = 0
FRAME_WORLD = 1
FRAME_ROBOT = 2

# might have to be bits..
AXIS_MASK_X = 1
AXIS_MASK_Y = 2
AXIS_MASK_Z = 4
AXIS_MASK_V =  AXIS_MASK_X + AXIS_MASK_Y + AXIS_MASK_Z

AXIS_MASK_WX = 8
AXIS_MASK_WY = 16
AXIS_MASK_WZ = 32
AXIS_MASK_W = AXIS_MASK_WX + AXIS_MASK_WY + AXIS_MASK_WZ 

def TransEye():
    T = np.eye(4)
    
    return T

def TransMatrix(p):
    T = TransEye()
    T[-1,:2] =  p
    return T

def initRot(pRot):
    T = TransEye()
    cosRot = np.cos(pRot)
    sinRot = np.sin(pRot)
    
    return T,cosRot,sinRot

def RotX(pRotX):
    T, cosRot, sinRot = initRot(pRotX)

    T[[1,2],[1,2]] = cosRot # broadcasting hehe
    T[[1,2],[2,1]] = -sinRot, sinRot

    return T

def RotY(pRotY):
    T, cosRot, sinRot = initRot(pRotY)

    T[[0,2],[0,2]] = cosRot
    T[[0,2],[2,0]] = sinRot, -sinRot

    return T

def RotZ(pRotZ):
    T, cosRot, sinRot = initRot(pRotZ)

    T[[0,1],[0,1]] = cosRot
    T[[1,0],[0,1]] = sinRot, -sinRot

    return T

""" 
# Axis Mask
# {POSITION 7, ROTATION 56, BOTH 63}
eyeTransform = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])

frame = 0
axisMask = 7
useSensorValues = 0

effectorList = []
pathList = []

# -- do the motion --
effector = 'LArm' # {Head, LArm, LLeg, RLeg, RArm, Torso}
dz = 0.01 # meters 
timeList = [1] # seconds
effectorList.append(effector)

# Transformation matrix 
# turn into np.array its unfolded into a 16 list item 
currentPos = motionProxy.getTransform(effector, frame, useSensorValues)
currentPos = np.array(currentPos).reshape(4,4)

# want to stay in current frame {0}
# so targetPost_{0} = currentPos_{0} * R
T = TransMatrix([0,0,dz]) 
targetPos = currentPos * T
pathList.append(targetPos)

# should work...
motionProxy.transformInterpolations(effectorList, frame, pathList, axisMask, timeList)

"""