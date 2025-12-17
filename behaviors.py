from core import get_session, get_service, get_objDetection_model, set_parser
from actions import *
from motion import *
import time
import cv2

from sshkeyboard import listen_keyboard_manual
import asyncio

## finished behaviors
def restNao(session):
    '''
    place nao in rest postion (3 point contact with floor) 
    '''
    postureService = get_service(session, 'ALRobotPosture')
    postureService.goToPosture("Sit",0.5)

    setStiffnesses(session, "Body", 0.0)


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
    Rotate the head around the desired Y(pitch) and Z(yaw) axis.
    With the option to return the head to its initial rotation 
    '''
    useSensors = False
    names = ['HeadYaw','HeadPitch']

    motionProxy = get_service(session, 'ALMotion')
    wPs = motionProxy.getAngles(names, useSensors)
    wPs = [round(x, 5) for x in wPs]
    
    # motionProxy.setStiffnesses(names , [1 ,1])
    
    # go to first position 
    motionProxy.setAngles(names, wPt, fractionMaxSpeed)
    #waitForAngles(wPt, motionProxy, names, useSensors)
 
       # if comeBack return to first position
    if comeBack:  
        motionProxy.setAngles(names, wPs, fractionMaxSpeed)
        waitForAngles(wPs, motionProxy, names, useSensors)

    # turn off stiffnesse
    # motionProxy.setStiffnesses(names, [0,0])

# break down into two functions:
#  one get image and predicts
#  second one takes image and turn head 

def followObjects(session):
    ledGroup = 'FaceLeds'
    ledService = get_service(session,'ALLeds')

    videoService = get_service(session, 'ALVideoDevice')
    unsubscribeNaoCam(videoService)
    videoClient = subscribeNaoCam(videoService)

    motionProxy = get_service(session, 'ALMotion')
    motionProxy.wakeUp()

    # old method
    #   frame = FRAME_ROBOT
    #   effector = 'Head'
    #   axisMask = AXIS_MASK_WY + AXIS_MASK_WZ
    fractionMaxSpeed = 0.1
    img,_ = getNaoImage(videoService, videoClient)
    img = np.array(img)
    # write to video
    H, W, _ = img.shape
    fps=15
    codec="mp4v"
    output_path = 'output_face.mp4'

    fourcc = cv2.VideoWriter_fourcc(*codec)
    out = cv2.VideoWriter(output_path, fourcc, fps, (W, H))

    model = get_objDetection_model('/mnt/c/users/multimaster/P2_yolo_dataset.pt')
    ledService.fadeRGB(ledGroup,'red',0.01)
    font = cv2.FONT_HERSHEY_SIMPLEX


    useSensors = False
    names = ['HeadYaw','HeadPitch']

    while True:
        try:
            img,_ = getNaoImage(videoService, videoClient)
            obj, boxes= predictNaoImage(model, img)

            img = np.array(img)
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

            if obj is not None:
                ledService.fadeRGB(ledGroup,'blue',0.01)
                xywhn = boxes.xywhn[0].tolist()
                xyxy = boxes.xyxy[0].tolist()
                x,y = xywhn[0:2]

                ### ADD FACE AND CHANGE COLOR OF BUTTON WHEN RECOGNIZE
                ### ALSO CHANGE TO getTransforms 

                # use default camera index unless it is defined when subscribing
                wPt = videoService.getAngularPositionFromImagePosition(0, [round(x,2),round(y,2)])
                B = motionProxy.getAngles(names, useSensors)
                info = f'{x:.2f},{y:.2f},{obj},{wPt[0]:.2f},{wPt[1]:.2f},{B[0]:.2f},{B[1]:.2f}'
                print(info)

                moveHead(session, wPt, fractionMaxSpeed, False)
                xyxy = [int(n) for n in xyxy]
                #img = cv2.putText(img, info, (10,30), font, 1, (255,0,0),0,cv2.LINE_AA)
                cv2.rectangle(img, xyxy[:2], xyxy[2:], (0,0,255),1)
                ledService.fadeRGB(ledGroup,'white',0.05)

                # old method
                #   T = TransEye()
                #   RotT = T @ RotZ(wP[1]) @ RotY(wP[0]-0.01)
                #   RotTv = RotT.reshape(-1).tolist()
                #   motionProxy.getTransforms(effector, frame, RotTv, factionMaxSpeed, axisMask)
            # write image
            out.write(img)

        except KeyboardInterrupt:
            setStiffnesses(s,"Body",0.0)
            out.release()
            break
        

### Development / debugging 
def extendArm(session, comeback):
    ## TESTING METHOD ##
    postureService = get_service(session, 'ALRobotPosture')
    motionProxy = get_service(session, 'ALMotion')
    motionProxy.wakeUp()

    names = motionProxy.getBodyNames("LArm")
    print(names)
    postureService.goToPosture("Stand",0.5)

    chainName = "LShoulderPitch"
    frame     = FRAME_TORSO
    useSensors = False
    fractionMaxSpeed = 0.2
    axisMask = AXIS_MASK_WZ
    
    wPt = [0]

    #motionProxy.setAngles(chainName, wPt, fractionMaxSpeed)
    #waitForAngles(wPt, motionProxy, chainName, useSensors)
    ##ts = motionProxy.getTransform(chainName, frame, useSensors)
    #ts = Transform(ts)
    #tt = ts @ TransRot([0,-np.pi/4,0,0,0,0])

    #print(tt.matrix)
    #print(tt.vector)
    #motionProxy.setTransforms(chainName, frame, tt.vector, fractionMaxSpeed, axisMask)
    #waitForTransform(tt, motionProxy, chainName, frame, useSensors)
    

def point(session):

    effectorList = ['LShoulderPitch']
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
    print(s)

    if args.behavior == 0:
        comeBack = True
        wP = [0.3,-0.3]
        fractionMaxSpeed = 0.1
        moveHead(s, wP, fractionMaxSpeed, comeBack,)
    elif args.behavior == 1:
        followObjects(s)
    elif args.behavior == 2:
        extendArm(s, True)
    elif args.behavior == 3:
        followObjects(s)
    elif args.behavior == 4:
        restNao(s)
    elif args.behavior == 5:
        #point(s)
        setStiffnesses(s, 'Body', 0)
    if args.OFF:
        turnNaoOFF(s)
        











