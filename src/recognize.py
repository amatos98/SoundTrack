'''
Created on Oct 25 , 2018

@author: Alexander Matos
'''



import pyaudio

import src.parse as parse 
import src.fingerprint as fingerprint 
import numpy as np
from email.mime import audio
from builtins import int




class BaseRecognizer(object):
    '''
    classdocs
    '''

    def __init__(self, shazam):
        '''
        Constructor
        '''
        self.shazam = shazam
        self.fs = fingerprint.DEFAULT_FS
        
        
    def recognize_helper(self, *audio_data):
        matches = []
        for e in audio_data:
            matches.extend(self.shazam.get_matches(e, fs = self.fs))
        return self.shazam.compare_matches(matches)
    
    
    
    
    
class MicrophoneRecognizer(BaseRecognizer):
    CHUNK = 8192
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    
    def __init__(self, shazam):
        super(MicrophoneRecognizer, self).__init__(shazam)
        self.audio = pyaudio.PyAudio()
        self.sound_data = []
        self.recorded = False
        self.rate = MicrophoneRecognizer.RATE
        self.chunk_size = MicrophoneRecognizer.CHUNK
        self.channels = MicrophoneRecognizer.CHANNELS
        self.stream = None
        
        
    def record(self, channels= CHANNELS, rate = RATE , chunksize= CHUNK):
        self.chunk_size = chunksize
        self.channels = channels
        self.recorded = False
        self.rate = rate
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            
        self.stream = self.audio.open(
                format = self.FORMAT,
                 channels = channels,
                rate = rate, 
                input = True, 
                frames_per_buffer = chunksize
            )
            
            
        self.sound_data = [[] for i in range(channels)]
            
    def stop_listening(self):
        self.stream.stop_stream()
        self.stream.close()
        self.stream = None
        self.recorded = True
            
        
    def process_recording(self):
        info = self.stream.read(self.chunk_size)
        count = np.fromstring(info, np.int16)
        for ch in range(self.channels):
            self.sound_data[ch].extend(count[ch::self.channels])
                
                
                
    def check_if_recording(self):
        return self.recognize_helper(*self.sound_data)
                
            
        
    def recognize(self, seconds = 10):
        self.record()
        for i in range(0, int(self.rate / self.chunk_size * int(seconds))):
            self.process_recording()
        self.stop_listening()
        return self.check_if_recording()
    


        
        
        
        
        
        
        
        
        
        
        