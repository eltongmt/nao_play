from core import get_session, get_service, get_objDetection_model, set_parser
from actions import *
import time
import keyboard

def recognizeObjects(session):
    
    videoService = get_service(session, 'ALVideoDevice')
    videoClient = subscribeNaoCam(videoService)
    textService = get_service(session, 'ALTextToSpeech')

    model = get_objDetection_model('')
    valid = True

    naoSpeak(textService, 'Show me some objects!')
    while valid:
        img,_ = getNaoImage(videoService, videoClient)

        names,_ = predictNaoImage(model,img)

        # say detected object name
        if len(names) > 0:
            name = names[[0]]
            naoSpeak(textService, name)
        
        # give window to break program 
        while time.time() - startTime < 2:
            startTime = time.time()
            if keyboard.is_pressed('z'):
                valid = False
            time.sleep(0.01)
    naoSpeak(textService, 'okay bye')



if __name__ == "__main__":
    parser = set_parser()
    parser.add_argument('--behavior', type='int',default=0)

    args = parser.parse_args()
    s = get_session(args)

    if args.behavior == 0:
        recognizeObjects(s)










