from core import get_session, get_service, get_objDetection_model, set_parser
from actions import *
import time
import keyboard

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

def moveHead():
    pass

if __name__ == "__main__":
    parser = set_parser()
    parser.add_argument('--behavior', type=int,default=0)

    args = parser.parse_args()
    s = get_session(args)

    if args.behavior == 0:
        recognizeObjects(s)










