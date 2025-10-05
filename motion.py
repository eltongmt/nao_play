import numpy as np

# frame constants 
FRAME_TORSO = 0
FRAME_WORLD = 1
FRAME_ROBOT = 2

# indicates target translations 
AXIS_MASK_X = 1
AXIS_MASK_Y = 2
AXIS_MASK_Z = 4
AXIS_MASK_V =  AXIS_MASK_X + AXIS_MASK_Y + AXIS_MASK_Z

AXIS_MASK_WX = 8
AXIS_MASK_WY = 16
AXIS_MASK_WZ = 32
AXIS_MASK_W = AXIS_MASK_WX + AXIS_MASK_WY + AXIS_MASK_WZ 


def TransformEye():
    '''
    return identity transformation matrix 
    where R is eye 3x3 and p = [0,0,0]

            [1  0  0  0]
    T_{i} = [0  1  0  0] = [R p]
            [0  0  1  0]   [0 1]
            [0  0  0  1]

    '''
    return np.eye(4)


def Trans(p):
    '''
    transformation matrix where R
    is eye and p = p (translation only)

    pT = [R_{I} p]
        [0     1]
    '''
    pT = TransformEye()
    pT[:3,-1] =  p
    return pT


def initRot(pRot):
    '''
    helper function to create rotation 
    matrices 
    '''
    T = TransformEye()
    cosRot = np.cos(pRot)
    sinRot = np.sin(pRot)
    
    return T,cosRot,sinRot


def RotX(pRotX):
    """
    transformation with rotation around x axis
        [1      0               0]
    Rx = [0  cos(pRotX)  -sin(pRotX)]
        [1  sin(pRotX)  cos(pRotX)]

    p = [0  0  0]
        
    T = [Rx p]
        [0  1]
    """
    T, cosRot, sinRot = initRot(pRotX)

    T[[1,2],[1,2]] = cosRot # broadcasting hehe
    T[[1,2],[2,1]] = -sinRot, sinRot

    return T


def RotY(pRotY):
    """
    transformation with rotation around y axis
        [cos(pRotY)   0  sin(pRotY)]
    Ry = [0            1           0]
        [-sin(pRotY)  0  cos(pRotY)]

    p = [0  0  0]
        
    T = [Ry p]
        [0  1]
    """
    T, cosRot, sinRot = initRot(pRotY)

    T[[0,2],[0,2]] = cosRot
    T[[0,2],[2,0]] = sinRot, -sinRot

    return T


def RotZ(pRotZ):
    """
    transformation with rotation around z axis
        [cos(pRotZ)   -sin(pRotZ)  0]
    Rz = [sin(pRotZ)   cos(pRotZ)   0]
        [0            0            1]

    p = [0  0  0]
        
    T = [Rz p]
        [0  1]
    """
    T, cosRot, sinRot = initRot(pRotZ)

    T[[0,1],[0,1]] = cosRot
    T[[1,0],[0,1]] = sinRot, -sinRot

    return T


def TransRot(sV):
    """
    transformation matrix rotated around w and 
    translated to v

    w = [wX wY wZ]
    v = [x y z]

    sV (spatial veloctity) = [w]
                            [v]
    """
    rotTx = RotX(sV[0])
    rotTy = RotY(sV[1])
    rotTz = RotZ(sV[2])
    pT = Trans(sV[3:])

    H = pT @ rotTz @ rotTy @ rotTx
    return H


class Transform:
    """
    Define transform class to easily go from
    (4,4) for operations to (,16) for actual
    processing 
    """
    def __init__(self, T):
        if isinstance(T, np.ndarray):
            self.matrix = T
            self.vector = self.matrix.reshape(-1)
        elif isinstance(T, list):
            self.vector = T
            self.matirx = np.array(self.vector).reshape(4,4) 
        else:
            raise Exception(f'type{T} is not a valid data type')
        
    def __matmul__(self, B):
        if isinstance(B, Transform):
            return np.dot(self.matrix, B.matrix)
        elif isinstance(B, np.ndarray):
            return np.dot(self.matrix, B)
        else:
            raise Exception(f'matmul is not defined for transform and {type(B)}')
    
    