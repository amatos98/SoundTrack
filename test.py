import warnings
import json
warnings.filterwarnings("ignore")

from src import Shazam
from src.recognize import MicrophoneRecognizer

# load config from a JSON file (or anything outputting a python dictionary)
with open("SoundTrack.cnf") as f:
    config = json.load(f)

if __name__ == '__main__':

    # create a Dejavu instance
    s = Shazam(config)

    # Fingerprint all the mp3's in the directory we give it
    s.fingerprint_folder(r"C:\Users\Alexander Matos\Documents\Sidify Music Converter", [".wav"])


    # Or recognize audio from your microphone for `secs` seconds
    secs = 10
    song = s.recognize(MicrophoneRecognizer, seconds=secs)
    if song is None:
        print ("Nothing recognized -- did you play the song out loud so your mic could hear it?")
    else:
        print ("From mic with %d seconds we recognized: %s\n" % (secs, song))
