from core import get_session, get_service, get_objDetection_model, set_parser
from actions import *
from motion import *
import time
import cv2

def turnNaoOFF(session):
    motionProxy = get_service(session, 'ALMotion')
    systemProxy = get_service(session, 'ALSystem')
    motionProxy.rest()

    systemProxy.shutdown()

def restNao(session):
    postureService = get_service(session, 'ALRobotPosture')
    motionProxy = get_service(session, 'ALMotion')

    postureService.goToPosture("Sit",0.5)
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
            RotT = T @ RotZ(wP[1]) @ RotY(wP[0])
            RotTv = RotT.reshape(-1).tolist()

            motionProxy.setTransforms(effector, frame, RotTv, factionMaxSpeed, axisMask)

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

def moveHead(session):
    # need to take into account pitch and yaw combo constrains 
    pass 

def turnHead(session):

    pathList = []
    frame = FRAME_TORSO
    motionProxy = get_service(session, 'ALMotion')
    motionProxy.wakeUp()

    intIf, targetIf, effectorList = calHeadPos(motionProxy, [-0.2,0],frame, useSensorValues=True)
    axisMask = AXIS_MASK_WY

    timeList = [2],#4]
    pathList.append(targetIf.tolist())
    #pathList.append(intIf)

    motionProxy.transformInterpolations(effectorList, frame, pathList, axisMask, timeList)
    
    motionProxy.setStiffnesses("Body", 0.0)


def holdHead(session):
    # figure this one out
    # why is it not working 

    wP = [0.2,0]
    motionProxy = get_service(session, 'ALMotion')
    motionProxy.wakeUp()

    frame = FRAME_ROBOT
    effector = 'Head'

    factionMaxSpeed = 0.5
    axisMask = AXIS_MASK_WY

    T = RotY(wP[0]).reshape(-1).tolist()
    Tf = RotY(-wP[0]).reshape(-1).tolist()

    motionProxy.setTransforms(effector, frame, T, factionMaxSpeed, axisMask)
    time.sleep(0.01)

    motionProxy.setTransforms(effector, frame, Tf, factionMaxSpeed, axisMask)

    time.sleep(0.01)
    motionProxy.setStiffnesses("Body", 0.0)



if __name__ == "__main__":
    parser = set_parser()
    parser.add_argument('--behavior', type=int,default=None)
    parser.add_argument('--OFF', type=bool,default=False)


    args = parser.parse_args()
    s = get_session(args)

    if args.behavior == 0:
        recognizeObjects(s)
    elif args.behavior == 1:
        turnHead(s)
    elif args.behavior == 2:
        holdHead(s)
    elif args.behavior == 3:
        followObjects(s)
    elif args.behavior == 4:
        resetNao(s, False)
    if args.OFF:
        turnNaoOFF(s)
        











