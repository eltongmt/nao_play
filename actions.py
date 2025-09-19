import qi
from time import time
import numpy as np
from PIL import Image


# -- ALTextToSpeech --
def naoSpeak(textService, text='connected to text service'):
    '''
    Make nao say text using qi synthesizer 
    '''
    textService.setLanguage('English')
    textService.say(text)

    return True

# -- ALVideoService -- 
def getNaoImage(videoService, videoClient):
    '''
    Get an image data from nao and transform it a 
    numpy array 
    '''

    t0 = time()
    # get data from nao 
    naoImage = videoService.getImageRemote(videoClient)
    t1 = time()

    # Get the image size and binary array.
    imageWidth = naoImage[0]
    imageHeight = naoImage[1]
    # binary image array 
    array = naoImage[6]
    imageStream = bytearray(array)

    # Create a PIL Image from binary.
    img = Image.frombytes('RGB', (imageWidth, imageHeight), imageStream)
    

    return img, t1 - t0

def unsubscribeNaoCam(videoService):
    '''
    The video client can only be connected to a limited number
    of services, use this to clear inactive services. 
    '''

    subs = videoService.getSubscribers()

    for sub in subs:
        videoService.unsubscribe(sub)
        print(f'{sub} unsubscribed from videoService')

    return True


def subscribeNaoCam(videoService, **kwargs):
    '''
    Valid parameters can be found @ http://doc.aldebaran.com/2-1/family/robots
    /video_robot.html#cameraresolution-mt9m114
    Default:
        cameraIndex = top camera (0)
        resolution = 160x120px (8)
        colorSpace = BGR (13)
    '''
    defaultArgs = {'cameraIndex':0,'resolution':2,'colorSpace':11,'fps':5}
    
    # set default params 
    for arg in defaultArgs.keys():
        if arg not in kwargs:
            kwargs[arg] = defaultArgs[arg]

    videoClient = videoService.subscribeCamera('python_client', kwargs['cameraIndex'],kwargs['resolution'],
						kwargs['colorSpace'],kwargs['fps'])

    return videoClient


# -- DIObjDetection -- 
def predictNaoImage(model, naoImage):
    '''
    Use yolo to detect objects 
    '''

    results = model.predict(naoImage, conf=0.50, verbose=False)
    results = results[0]
    names = results.names

    cls = results.boxes.cls
    print(cls)

    if cls.numel() > 0:
        obj = names[cls[0].item()]
    else:
        obj = 0
    return obj
    
# -- ALMotion -- 
def moveHead(motionProxy, wP):
    effector = 'Head'

    timeList = [1]
    effector

    

