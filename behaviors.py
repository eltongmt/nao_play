from core import get_session, get_service, get_objDetection_model, set_parser
from actions import *
from motion import *
import time
import cv2

## finished behaviors
def restNao(session):
    '''
    place nao in rest postion (3 point contact with floor) 
    '''
    postureService = get_service(session, 'ALRobotPosture')
    motionProxy = get_service(session, 'ALMotion')

    postureService.goToPosture("Sit",0.5)
    motionProxy.setStiffnesses("Body", 0.0)


def turnNaoOFF(session):
    '''
    move nao to a safe rest postion then turn off
    '''
    motionProxy = get_service(session, 'ALMotion')
    systemProxy = get_service(session, 'ALSystem')
    motionProxy.rest()

    systemProxy.shutdown()


def setStiffnesses(session, name, stiffnesse):
    '''
    use to relax part of nao
    '''
    motionProxy = get_service(session, 'ALMotion')
    motionProxy.setStiffnesses(name, stiffnesse)


def moveHead(session, wPt, fractionMaxSpeed, comeBack):
    '''
    Rotate the head around the desired Z(yaw) and Y(pitch) axis.
    With the option to return the head to its initial rotation 
    '''

    motionProxy = get_service(session, 'ALMotion')
    motionProxy.setStiffnesses('Head', 1)

    names = ['HeadYaw','HeadPitch']
    useSensors = False
    wPs = motionProxy.getAngles(names, useSensors)

    # go to first position 
    motionProxy.setAngles(names, wPt, fractionMaxSpeed)
    waitForAngles(wPt, motionProxy, names, useSensors)
   
   # if comeBack return to first position
    if comeBack:
        motionProxy.setAngles(names, wPs, fractionMaxSpeed)
        waitForAngles(wPs, motionProxy, names, useSensors)

    # turn off stiffnesse
    motionProxy.setStiffnesses('Head', 0.0)


### Development / debugging 
def point(session):

    effectorList = ['LArm']
    frame = FRAME_TORSO
    useSensorValues = False # should this be false? 

    pathList = []
    frame = FRAME_TORSO
    motionProxy = get_service(session, 'ALMotion')
    motionProxy.wakeUp()

    currentPos = motionProxy.getTransform(effectorList[0], frame, useSensorValues)
    currentPos = np.array(currentPos).reshape(4,4)

    T = TransMatrix([0,0,0.05])
    print(currentPos)
    print(T)
    print(currentPos @ T)
    print(T @ currentPos)
    targetIf = T @ currentPos
    
    axisMask = AXIS_MASK_V

    timeList = [10, 20]
    pathList.append(targetIf.reshape(-1).tolist())
    pathList.append(currentPos.reshape(-1).tolist())

    motionProxy.transformInterpolations(effectorList, frame, pathList, axisMask, timeList)
    motionProxy.setStiffnesses("Body", 0.0)


def followObjects(session):

    videoService = get_service(session, 'ALVideoDevice')
    unsubscribeNaoCam(videoService)
    videoClient = subscribeNaoCam(videoService)

    motionProxy = get_service(session, 'ALMotion')
    motionProxy.wakeUp()

    frame = FRAME_ROBOT
    effector = 'Head'

    factionMaxSpeed = 0.8
    axisMask = AXIS_MASK_WY + AXIS_MASK_WZ

    model = get_objDetection_model('/mnt/c/users/multimaster/P2_yolo_dataset.pt')
    while True:
        img,_ = getNaoImage(videoService, videoClient)
    

        obj, xywhn = predictNaoImage(model, img)

        if obj is not None:
            x,y = xywhn[0:2]

            print(x,y)
            print(obj)

            ### ADD FACE AND CHANGE COLOR OF BUTTON WHEN RECOGNIZE
            ### ALSO CHANGE TO getTransforms 

            # use default camera index unless it is defined when subscribing
            wP = videoService.getAngularPositionFromImagePosition(0, [x,y])

            T = TransEye()
            RotT = T @ RotZ(wP[1]) @ RotY(wP[0]-0.01)
            RotTv = RotT.reshape(-1).tolist()

            # could do something like like while the effector is not in position 
            # keep sleeping
            motionProxy.getTransforms(effector, frame, RotTv, factionMaxSpeed, axisMask)

            time.sleep(5)
        else:
            print(None)
        print()
        
        #motionProxy.setStiffnesses("Body", 0.0)
    motionProxy.rest()

def recognizeObjects(session):
    
    videoService = get_service(session, 'ALVideoDevice')
    unsubscribeNaoCam(videoService)
    videoClient = subscribeNaoCam(videoService)
    textService = get_service(session, 'ALTextToSpeech')

    model = get_objDetection_model('/mnt/c/users/multimaster/P2_yolo_dataset.pt')
    valid = True

    naoSpeak(textService, 'Show me some objects!')
    while valid:
        img,_ = getNaoImage(videoService, videoClient)

        name = predictNaoImage(model,img)
        print(name)

        # say detected object name
        if name:
            naoSpeak(textService, name)
        
        time.sleep(1)
  
    naoSpeak(textService, 'okay bye')


def turnHead(session):

    pathList = []
    frame = FRAME_TORSO
    motionProxy = get_service(session, 'ALMotion')
    motionProxy.wakeUp()

    intIf, targetIf, effectorList = calHeadPos(motionProxy,[0.1,0],frame, useSensorValues=True)
    axisMask = AXIS_MASK_WY

    timeList = [2, 4]
    pathList.append(targetIf.tolist())
    pathList.append(intIf)

    print(np.array(intIf).reshape(4,4))
    motionProxy.transformInterpolations(effectorList, frame, pathList, axisMask, timeList)

    motionProxy.setStiffnesses("Body", 0.0)


def defaultVals(session):
    chains = ["Head", "LArm", "LLeg", "RLeg", "RArm"]

    postureService = get_service(session, 'ALRobotPosture')
    motionProxy = get_service(session, 'ALMotion')
    
    postureService.goToPosture("Stand",0.2)
    config = motionProxy.getRobotConfig()
    print(config)

    useSensorValues = False
    frame = FRAME_TORSO

    for chain in chains:
        cP = motionProxy.getTransform(chain, frame, useSensorValues)
        cP = Transform(cP)
        print(f'home configuration for {chain}\n: {cP.matrix}')


if __name__ == "__main__":
    parser = set_parser()
    parser.add_argument('--behavior', type=int,default=None)
    parser.add_argument('--OFF', type=bool,default=False)


    args = parser.parse_args()
    s = get_session(args)

    if args.behavior == 0:
        wP = [-0.1, -0.2]
        comeBack = True
        fractionMaxSpeed = 0.2

        moveHead(s, wP, comeBack, fractionMaxSpeed)
    elif args.behavior == 1:
        turnHead(s)
    elif args.behavior == 2:
        holdHead(s)
    elif args.behavior == 3:
        followObjects(s)
    elif args.behavior == 4:
        restNao(s)
    elif args.behavior == 5:
        #point(s)
        setStiffnesses(s, 'Head', 0)
    if args.OFF:
        turnNaoOFF(s)
        











