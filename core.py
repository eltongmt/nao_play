import qi
import argparse
from ultralytics import YOLO

def set_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', type=str, default='127.0.0.1',
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument('--port', type=int, default=9559,
                        help='Naoqi port number')
    return parser

def get_session(args):
    """
        -- Connect to nao robot --

        Base workflow for this:
            s = qi.Session()
            s.connect("tcp://192.168.1.65:9559")

            s.service("Foo")
    """
    # -- Code modified from http://doc.aldebaran.com/2-5/naoqi/motion/..
    # -- control-joint-api.html#ALMotionProxy::setAngles__AL::ALValueCR.AL::ALValueCR.floatCR 
    session = qi.Session()
    
    try:
        session.connect("tcp://" + args.ip + ":" + str(args.port))
        print(f"Connected to Naoqi at ip {args.ip} on port {args.port}")
        
    except RuntimeError:
        print(f"Can't connect to Naoqi at ip {args.ip} on port {args.port}")
        session = []
    return session

def get_service(session, service_name):
    """
        -- Get a proxy to a service/module --
    
        supported services:
        ALTextToSpeech -> produce speech
        ALVideoDevice  -> get images
        ALRobotPosture -> whole body preset translation 

        Working on (might not happen)
        ALMotion -> individual control 
    
    """
    validServices = ["ALTextToSpeech","ALVideoDevice","ALRobotPosture"]

    if session not in validServices:
        print(f"service : {service_name} is not supported.")
        print("Choose from: ")
        for validService in validServices:
            print(f" {validService}")
    try:
        service = session.service(service_name)
        print(f"Sucessfully subscrbied to module {service_name}")
    except Exception as e:
        print(e)

    return service
        
def get_objDetection_model(modelPath, device=0):
    model = YOLO(modelPath,device=device)
    
    return model