'''
Created on Nov 11, 2018

@author: alex
'''
import src.parse as parse
import os 
import sys
from src.database import return_db, Database
import src.fingerprint

class Shazam(object):
    '''
    classdocs
    
    '''
    SONG_ID = "song_id"
    SONG_NAME = "song_name"
    OFFSET = "offset"


    def __init__(self, config):
        '''
        Constructor
        '''
        super(Shazam,self).__init__()
        self.config = config
        
        # Initialize database of fingerprinted songs
        new_db = return_db(config.get("db_type", None))
        self.db = new_db(**config.get("database", {}))
        self.db.launch()
        
        self.return_fp_songs()
        
        
        
    def fingerprint_folder(self, directory_path, extensions):
        
        to_fingerprint = [] 
        for file, _ in parse.import_dir(directory_path,extensions):
            if parse.generate_hash(file) not in self.song_hashes:  
                to_fingerprint.append(file)
    
    
        
        iterator = list(map(fingerprint_helper, to_fingerprint))    
        
        for target_file in iterator:
            song_name, hash, file_hash = target_file
            hashes_set = set(hash)
            song_id = self.db.add_song(song_name, file_hash)
            
            self.db.insert_hashes(song_id, hashes_set)
            self.db.fingerprint_song(song_id) # set fingerprinted song to true 
            self.return_fp_songs()
            
            
        
    def fingerprint_file(self, file_loc, song_name=None):
        ''' Adds audio_track to dictionary, one song at a time 
        
             @param string location of audio file to be imported 
        '''
        
        track_name = parse.get_songname(file_loc)
        
        # check if file has been fingerprinted 
        song_hash = parse.generate_hash(file_loc)
        song_name = parse.get_songname(file_loc)
        
        if song_hash in self.song_hashes:  
            print("%s is already fingerprinted and is in database" % song_name)
        else:
            
            song_name, hashes, file_hash = fingerprint_helper(file_loc, song_name=song_name)
            
            song_id = self.db.add_song(song_name, file_hash)
            
            self.db.insert_hashes(song_id, hashes)
            self.db.fingerprint_song()
            self.db.return_fp_songs()
        
        
        
        
        
    def recognize(self, recognizer, *options, **menu):
        rec = recognizer(self)
        return rec.recognize(*options, **menu)
        
        
        
    def return_fp_songs(self):
        self.songs = self.db.get_fingerprinted_songs()
        self.song_hashes = set()
        for s in self.songs:
            song_hash = s[Database.FIELD_SHA1_FILE]
            self.song_hashes.add(song_hash)
        
        
        

            

    def get_matches(self, samples, fs = fingerprint.DEFAULT_FS):
        hashes = fingerprint.fingerprint(samples, fs = fs)
        return self.db.collect_matches(hashes)  
 
 
 
    def compare_matches(self, matches):
        ''' Determine which hash matches have the same time as other matches
        
        For each address in the record, we get the associated value of the song and we compute delta = absolute time of the anchor in the record
         absolute time of the anchor in the song and put the delta in a list of delta.
        
        
        It is possible that the address in the record is associated with multiples values in the song (i.e. multiple points in different target zones of the song), 
        in this case we compute the delta for each associated values and we put the deltas in the list of delta'''
        
    
        
        time_offsets = {}
        maximum_count = 0
        greatest = 0
        songID = -1
        
        for tuple in matches:
            # the value: (song_id , time delta)
            id, delta = tuple
             
            if delta not in time_offsets:
                time_offsets[delta] = {}
            if id not in time_offsets[delta]:
                time_offsets[delta][id] = 0
            time_offsets[delta][id] += 1
            
            if time_offsets[delta][id] > maximum_count:
                greatest = delta 
                maximum_count = time_offsets[delta][id]
                songID = id
                
                
        # proceed to identify the song
        track = self.db.get_song(songID)
        
        if track:
            song_name = track.get(Shazam.SONG_NAME, None)
        else:
            return None
        
        
        # return match info
        
        track = {
            
            Shazam.SONG_ID: song_ID,
            Shazam.SONG_NAME: song_name,
            Shazam.OFFSET: int(greatest),
            Database.FIELD_SHA1_FILE : track.get(Database.FIELD_SHA1_FILE, None),
                 
        }      
                
        return track     
                
                
                
def fingerprint_helper(filename, limit = None, song_title= None):
    ''' This helper function takes the audio data from the song
        and fingerprints the song'''
    songname, extension = os.path.splitext(os.path.basename(filename))
    song_name = songname or song_title 
        
    final = []
    channels, framerate, hash_file = parse.analyze(filename)
    num_channels = len(channels)
        
    for num, channel in enumerate(channels):
        # Fingerprinting the song 
        hashes = fingerprint.fingerprint(channel)   
        final.append(list(hashes))
        #final |= set(hashes)
            
    return songname, final, hash_file
            
            
            

        
        
                
        