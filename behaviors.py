from core import get_session, get_service, get_objDetection_model, set_parser
from actions import *
from motion import *
import time
import keyboard


def followObjects(session):
    pass

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
        #img.save('test4.jpg')

        name = predictNaoImage(model,img)
        print(name)

        # say detected object name
        if name:
            naoSpeak(textService, name)
        
        time.sleep(1)
        # give window to break program 
        #while time.time() - startTime < 2:
        #    if keyboard.is_pressed('z'):
        #        valid = False
        #    time.sleep(0.01)
    naoSpeak(textService, 'okay bye')

def moveHead(session):
    # need to take into account pitch and yaw combo constrains 
    pass 

def nodHead(session):

    pathList = []
    frame = FRAME_TORSO
    motionProxy = get_service(session, 'ALMotion')
    motionProxy.wakeUp()

    intIf, targetIf, effectorList = calHeadPos(motionProxy, [-0.2,0],frame, useSensorValues=True)
    axisMask = AXIS_MASK_WY

    timeList = [2,4]
    pathList.append(targetIf.tolist())
    pathList.append(intIf)

    motionProxy.transformInterpolations(effectorList, frame, pathList, axisMask, timeList)
    
    motionProxy.setStiffnesses("Body", 0.0)


def holdHead(session):
    # figure this one out
    # why is it not working 

    wP = [0.1,0]
    motionProxy = get_service(session, 'ALMotion')
    motionProxy.wakeUp()

    frame = FRAME_ROBOT
    effector = 'Head'

    factionMaxSpeed = 0.5
    axisMask = AXIS_MASK_WY

    T = RotY(wP[0]).reshape(-1).tolist()

    start = time.time()
    while time.time() - start < 10:
        print(time.time())
        motionProxy.setTransforms(effector, frame, T, factionMaxSpeed, axisMask)
        n = motionProxy.getTransform(effector, frame, True)
        print(np.array(n).reshape(4,4))
        time.sleep(0.01)

    time.sleep(5)
    motionProxy.setStiffnesses("Body", 0.0)




    


if __name__ == "__main__":
    parser = set_parser()
    parser.add_argument('--behavior', type=int,default=1)

    args = parser.parse_args()
    s = get_session(args)

    if args.behavior == 0:
        recognizeObjects(s)
    elif args.behavior == 1:
        turnHead(s)
    elif args.behavior == 2:
        holdHead(s)










