
import qi
from utils import get_session


s = get_session()

textService = s.service("ALTextToSpeech")
textService.setLanguage("English")

text = "Retrieves the latest image from the video source, applies eventual transformations to the image to provide the format requested by the vision module and send it as an ALValue through the network."


textService.say(text)
