import os
import sys
import json 
import warnings
import argparse
from argparse import RawDescriptionHelpFormatter

from src import Shazam

from src.recognize import MicrophoneRecognizer


CONFIG_FILE = "SoundTrack.cnf"

def init(configpath):
    ''' Load config from a JSON file '''
    
    try:
        with open(configpath) as f:
            config = json.load(f)
    except IOError as errno:
        print("Failed to open configuration: %s.")
        sys.exit(1)
            
    # Shazam instance
    return Shazam(config)
        
        
        
if __name__ == '__main__':
    p = argparse.ArgumentParser(description= "Song Detector",
                                 formatter_class=RawDescriptionHelpFormatter)
    p.add_argument('-c', '--config', nargs='?', help= 'Path to configuration file\n'
                                                      'Usages: \n'
                                                      '--config /path/to/config-file\n')
    p.add_argument('-f', '--fingerprint', nargs = '*', help = 'Fingerprint a directory of files\n' )
    
    p.add_argument('-r', '--recognize', nargs=2, help = 'Recognize audio playing through microphone ')

    args = p.parse_args()
    
    if not args.fingerprint and not args.recognize:
        p.print_help()
        sys.exit(0)
        
    configuration_file = args.config
    
    if configuration_file is None:
        configuration_file = CONFIG_FILE
    
    shazam = init(configuration_file)
    if args.fingerprint:
        # Fingerprint files in a folder 
        if len(args.fingerprint) == 2:
            folder = args.fingerprint[0]
            exten = args.fingerpritn[1]
            
            print("Fingerprinting all .%s files in the directory" %(exten, folder))
            shazam.fingerprint_folder()
            
        elif len(args.fingerprint) == 1:
            path = args.fingerprint[0]
            if os.path.isdir(path):
                print("Please specify an extension if desired")
                sys.exit(1)
            shazam.fingerprint_file(path)
            
            
    elif args.recognize:
        song = None
        audio = args.recognize[0]
        optional = args.recognize[1]
        
        if audio in ('mic', 'microphone'):
            song = shazam.recognize(MicrophoneRecognizer, seconds = optional)
            
        print(song)
        
        
        
    sys.exit(0)
    
        
    