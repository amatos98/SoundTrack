'''
Created on Nov 11, 2018

@author: alex
'''


from __future__ import absolute_import
import abc 


class Database(object):
    
    __metaclass__ = abc.ABCMeta
    '''
    Stores collection of fingerprinted songs from file in to a database. 
    '''
    FIELD_SHA1_FILE = 'sha1'
    FIELD_SONG_ID = 'song_id'
    FIELD_SONG_NAME = 'song_name'
    FIELD_HASH = 'hash'
    FIELD_OFFSET = 'offset'
    
    type = None

    def __init__(self):
        '''
        Constructor
        '''
        super(Database,self).__init__()
        
        
        
    @abc.abstractclassmethod
    def launch(self):
        
        ''' initializes database'''
        
        pass
            
    
        
    @abc.abstractclassmethod
    def empty(self):
        """
        Erases all fingerprinted data from the database 
        """    
        pass
    
    @abc.abstractclassmethod
    def num_songs(self):
        '''
        Returns the number of songs currently in the database. 
        '''
        pass
        
    @abc.abstractclassmethod    
    def num_fingerprints(self):
        '''
        Returns the number of fingerprints in the database.
        '''
        pass
    
    @abc.abstractclassmethod
    def fingerprint_song(self, song_id):
        ''' Fingerprint song specified by song_id
        
            song_id: Song identifier
        
        '''
    
        pass
    @abc.abstractclassmethod   
    def get_fingerprinted_songs(self):
        '''
        Returns all fingerprinted songs in the database
        '''
        pass
    
    @abc.abstractclassmethod
    def get_song_(self, song_id):
        '''
        Returns song by specified id 
        
        '''
        pass
    
    @abc.abstractclassmethod
    def insert(self, hash, song_id, offset):
        '''
        Insert a fingerprint in the database.
        
        hash: part of sha1 hash, in hexadecimal fromat 
        song_id: Song identifier 
        offset: anchor time or where hash originates
        
        '''
        pass
        
        
    @abc.abstractclassmethod
    def add_song(self, song_name):
        '''
        Adds a song name into the database, and returns the id of the song.
        
        name: name of the song
        '''
        pass
    
    @abc.abstractclassmethod    
    def get_fingerprints_pairs(self):
        '''
        Return all fingerprints in the database
        
        '''
        
        pass
    
    
    @abc.abstractclassmethod
    def query(self, hash):
        ''' 
        Return a matching fingerprinted songs that belong to hash
            of audio file as a parameter
            @return tuple 
            
        hash: part of sha1 hash, in hexadecimal format 
        
        '''
        pass
   
    
    @abc.abstractclassmethod
    def delete_unfingerprinted_songs(self):
        '''
        Delete songs that were not fingerprinted in the database. 
        '''
        pass
    
    
    @abc.abstractclassmethod
    def insert_hashes(self, song_id, hashes):
        '''
        Insert a collection of fingerprints in the database.
        
        song_id: Song identifier the fingerprints belong to
        
        hashes: A sequence of tuples in the format (hash, offset)
        -   hash: Part of a sha1 hash, in hexadecimal format
        - offset: Offset this hash was created from/at.
    
        '''
        pass
    
    @abc.abstractclassmethod
    def get_song_matches(self, hashes):
        '''
        Searches the database for pairs of (hash, offset) values.
        
        hashes: A sequence of tuples in the format (hash, offset)
        -   hash: Part of a sha1 hash, in hexadecimal format
        - offset: Offset this hash was created from/at.
        
        @return a sequence of (sid, offset_difference) tuples.
                      sid: Song identifier
        offset_difference: (offset - database_offset)
        '''
        
def return_db(db_type=None):
        
    db_type = db_type or "mysql"
    db_type = db_type.lower()
        
    for db_cls in Database.__subclasses__():
        if db_cls.type == db_type:
            return db_cls
    
    raise TypeError("Unsupported database")
    
#import default database
import src.database_sql

    