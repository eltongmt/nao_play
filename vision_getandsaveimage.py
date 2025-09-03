import qi
import argparse
import sys
import time
from PIL import Image
import cv2
import numpy as np

def get_naoImage(video_service, videoClient):

    t0 = time.time()
    naoImage = video_service.getImageRemote(videoClient)
    t1 = time.time()
    print ("acquisition delay ", t1 - t0)

    # Get the image size and pixel array.
    imageWidth = naoImage[0]
    imageHeight = naoImage[1]
    array = naoImage[6]
    image_stream = bytearray(array)

    # Create a PIL Image from our pixel array.
    im = Image.frombytes("RGB", (imageWidth, imageHeight), image_stream)
    im_np = np.array(im)
    #im_np = cv2.cvtColor(im_np, cv2.COLOR_RGB2BGR)

    return im_np

def clean_subscribers(video_service):
    subs = video_service.getSubscribers()

    for sub in subs:
        print(sub)
        video_service.unsubscribe(sub)


def display_naoCameraStream(session):
    """
    First get an image, then show it on the screen with PIL.
    """
    # Get the service ALVideoDevice.

    video_service = session.service("ALVideoDevice")

    clean_subscribers(video_service)

    cameraIndex = 0
    resolution = 8    # VGA
    colorSpace = 13   # RGB

    videoClient = video_service.subscribeCamera("python_client", cameraIndex, resolution, colorSpace, 5)

    t0 = time.time()
    while True:
        t1 = time.time()

        im = get_naoImage(video_service, videoClient)

        cv2.imshow("nao feed2", im)
        
        key = cv2.waitKey(1)  # Wait for a key event for 1 millisecond
        if key == ord('q'):  # Check if the pressed key is 'q'
            cv2.destroyAllWindows()  # Close all OpenCV windows
            break


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="192.168.1.65",
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")

    args = parser.parse_args()
    session = qi.Session()
    try:
        session.connect("tcp://" + args.ip + ":" + str(args.port))
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)

    display_naoCameraStream(session)
