'''
Created on Oct 25, 2018

@author: Alexander Matos

'''


import numpy as np
import src.wavio as wavio
from pydub import AudioSegment
import fnmatch

import os
from fnmatch import filter
from hashlib import sha1



def generate_hash(fpath, blocksize=2**20):
    ''' Small function to generate a hash to uniquely generate
    a file. Inspired by MD5 version here:
    http://stackoverflow.com/a/1131255/712997 '''
    
    s = sha1()

    with open(fpath, "rb" ) as f:
        while True:
            buf = f.read(blocksize)
            if not buf:
                break
            s.update( buf )
    return s.hexdigest().upper()


    
    





def analyze(file_name):
    ''' The functionality of this function reads 24-bit .wav files only
        and returns the data from within. 
        
        return (channels, samplerate) '''
    
    
    
    fr, _, audio_data = wavio.readwav(file_name)
    audio_data = audio_data.T
    audio_data = audio_data.astype(np.int16)
    
    channels = []
    for s in audio_data:
        channels.append(s)
        
        
    return channels, 44100, generate_hash(file_name)
    

def import_dir(path, extensions):
    extensions  = [e.replace(".", "") for e in extensions]
    for dirpath, dirname, files in os.walk(path):
        for exten in extensions:
            for f in fnmatch.filter(files, "*.%s" % exten):
                p = os.path.join(dirpath, f)
                yield(p, exten)
                
                
                
                
def get_songname(directory_path):
    ''' Attains songname from path of directory.
        Used to identify which songs have been fingerprinted in 
        the library'''
    
    return os.path.splitext(os.path.basename(directory_path))[0]
                    
                
                