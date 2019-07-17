'''
Created on Nov 11, 2018

@author: alex
'''
from __future__ import absolute_import
from src.database import Database
import queue

from itertools import zip_longest

import pymysql as mysql
from macpath import join
mysql.install_as_MySQLdb()

#import MySQLdb as mysql
#from _sqlite3 import Cursor
from src.parse import get_songname
from pymysql.cursors import DictCursor




class Database_SQL(Database):
    '''
    classdocs
    '''
    type = "mysql"
    
    #tables 
    FINGERPRINTS_TABLENAME = "fingerprints"
    SONGS_TABLENAME = "songs"

     
    #fields
    FINGERPRINTED_FIELD = "fingerprinted"
   
   
    # Creating tables 
     
    CREATE_FINGERPRINTS_TABLE = """
        CREATE TABLE IF NOT EXISTS `%s` (
             `%s` binary(10) not null,
             `%s` mediumint unsigned not null,
             `%s` int unsigned not null,
         INDEX (%s),
         UNIQUE KEY `unique_constraint` (%s, %s, %s),
         FOREIGN KEY (%s) REFERENCES %s(%s) ON DELETE CASCADE
    ) ENGINE=INNODB;""" % (
        FINGERPRINTS_TABLENAME, Database.FIELD_HASH,
        Database.FIELD_SONG_ID, Database.FIELD_OFFSET, Database.FIELD_HASH,
        Database.FIELD_SONG_ID, Database.FIELD_OFFSET, Database.FIELD_HASH,
        Database.FIELD_SONG_ID, SONGS_TABLENAME, Database.FIELD_SONG_ID
    )
     
     
    CREATE_SONGS_TABLE = """
        CREATE TABLE IF NOT EXISTS `%s` (
            `%s` mediumint unsigned not null auto_increment,
            `%s` varchar(250) not null,
            `%s` tinyint default 0,
            `%s` binary(20) not null,
        PRIMARY KEY (`%s`),
        UNIQUE KEY `%s` (`%s`)
    ) ENGINE=INNODB;""" % (
        SONGS_TABLENAME, Database.FIELD_SONG_ID, Database.FIELD_SONG_NAME, FINGERPRINTED_FIELD,
        Database.FIELD_SHA1_FILE,
        Database.FIELD_SONG_ID, Database.FIELD_SONG_ID, Database.FIELD_SONG_ID,
    )
   
   
   
    # inserts 
    INSERT_FINGERPRINT = """
        INSERT IGNORE INTO %s (%s, %s, %s) values
            (UNHEX(%%s), %%s, %%s);
    """ % (FINGERPRINTS_TABLENAME, Database.FIELD_HASH, Database.FIELD_SONG_ID, Database.FIELD_OFFSET)

    INSERT_SONG = "INSERT INTO %s (%s, %s) values (%%s, UNHEX(%%s));" % (
        SONGS_TABLENAME, Database.FIELD_SONG_NAME, Database.FIELD_SHA1_FILE)
    
    # selects
    SELECT = """
        SELECT %s, %s FROM %s WHERE %s = UNHEX(%%s);
    """ % (Database.FIELD_SONG_ID, Database.FIELD_OFFSET, FINGERPRINTS_TABLENAME, Database.FIELD_HASH)

    SELECT_MANY = """
        SELECT HEX(%s), %s, %s FROM %s WHERE %s IN (%%s);
    """ % (Database.FIELD_HASH, Database.FIELD_SONG_ID, Database.FIELD_OFFSET,
           FINGERPRINTS_TABLENAME, Database.FIELD_HASH)

    SELECT_ALL = """
        SELECT %s, %s FROM %s;
    """ % (Database.FIELD_SONG_ID, Database.FIELD_OFFSET, FINGERPRINTS_TABLENAME)

    SELECT_SONG = """
        SELECT %s, HEX(%s) as %s FROM %s WHERE %s = %%s;
    """ % (Database.FIELD_SONG_NAME, Database.FIELD_SHA1_FILE, Database.FIELD_SHA1_FILE, SONGS_TABLENAME, Database.FIELD_SONG_ID)

    SELECT_NUM_FINGERPRINTS = """
        SELECT COUNT(*) as n FROM %s
    """ % (FINGERPRINTS_TABLENAME)

    SELECT_UNIQUE_SONG_IDS = """
        SELECT COUNT(DISTINCT %s) as n FROM %s WHERE %s = 1;
    """ % (Database.FIELD_SONG_ID, SONGS_TABLENAME, FINGERPRINTED_FIELD)

    SELECT_SONGS = """
        SELECT %s, %s, HEX(%s) as %s FROM %s WHERE %s = 1;
    """ % (Database.FIELD_SONG_ID, Database.FIELD_SONG_NAME, Database.FIELD_SHA1_FILE, Database.FIELD_SHA1_FILE,
           SONGS_TABLENAME, FINGERPRINTED_FIELD)

    # drops
    DROP_FINGERPRINTS = "DROP TABLE IF EXISTS %s;" % FINGERPRINTS_TABLENAME
    DROP_SONGS = "DROP TABLE IF EXISTS %s;" % SONGS_TABLENAME

    # update
    UPDATE_SONG_FINGERPRINTED = """
        UPDATE %s SET %s = 1 WHERE %s = %%s
    """ % (SONGS_TABLENAME, FINGERPRINTED_FIELD, Database.FIELD_SONG_ID)

    # delete
    DELETE_UNFINGERPRINTED = """
        DELETE FROM %s WHERE %s = 0;
    """ % (SONGS_TABLENAME, FINGERPRINTED_FIELD)

    
    def __init__(self, **menu):
        '''
        Constructor
        '''
        super(Database_SQL,self).__init__()
        self.cursor = setup_cursor(**menu)
        self._menu = menu
    
    
    def launch(self):
        
        ''' creates fingerprints and songs tables for Shazam recognizer'''
        
        with self.cursor() as cur:
            cur.execute(self.CREATE_SONGS_TABLE)
            cur.execute(self.CREATE_FINGERPRINTS_TABLE)
            cur.execute(self.DELETE_UNFINGERPRINTED)
    
    
    
    def empty(self):
        ''' Clearing data in the tables by deleting the tables
            and calling setup to create empty new ones '''
        
        with self.cursor() as cur:
            cur.execute(self.DROP_SONGS)
            cur.execute(self.DROP_FINGERPRINTS)
         
        
        self.launch()
        
        
        
    def num_songs(self):
        ''' Returns the number of songs in the database that
            have been fingerprinted. '''
        with self.cursor() as cur:
            cur.execute(self.SELECT_UNIQUE_SONG_IDS)
        
        
    def add_song(self, song_name, hashed_file):
        '''
        Adds a song name into the database, and returns the id of the song.
        
        name: name of the song
        '''
        with self.cursor() as cur:
            cur.execute(self.INSERT_SONG, (song_name, hashed_file))
        
        
    def query(self, hash):
        ''' 
        Return a matching fingerprinted songs that belong to hash
            of audio file as a parameter
            @return tuple , which is a couple (anchor time, sID)
            
        hash: part of sha1 hash, in hexadecimal format 
        
        '''
        
        search = self.SELECT_ALL if hash is None else self.SELECT
        
        with self.cursor() as cur:
            cur.execute(search)
            for song_id, offset in cur:
                yield(song_id, offset)
        
        
        
    def get_song(self, song_id):
        '''Returns song name  by its ID'''
        
        with self.cursor(cursor_type = DictCursor) as cur:
            cur.execute(self.SELECT_SONG, (song_id, ))
            return cur.fetchone()
            
    
    
    def fingerprint_song(self, song_id):
        
        '''Sets a song's fingerprint bool val to TRUE or (1) '''
        with self.cursor() as cur:
            cur.execute(self.UPDATE_SONG_FINGERPRINTED, (song_id,))
    
    def get_fingerprinted_songs(self):
        
        ''' Return songs only if fingerprinted == TRUE'''        
        with self.cursor(cursor_type = DictCursor) as cur:
            cur.execute(self.SELECT_SONGS)
            for row in cur:
                yield row
                
            
            
    def num_fingerprints(self):
        ''' Returns the number of fingerprints in the database.'''
        
        with self.cursor() as cur:
            cur.execute(self.SELECT_NUM_FINGERPRINTS)
            for number, in cur:
                return number
            return 0
        
        
    def get_fingerprints_pairs(self):
        
        '''Return all fingerprints in the database.
        
          @return tuples
          
        '''
        return self.query(None)

    def insert_hashes(self, song_id, hashes):
        '''
          The fingerprint of each song will be a 
          [hash => (song_id, offset)] value, where offset is the
          absolute time of the anchor point minus the time
          at the start, which t = 0. 
          
          Store these fingerprints into the database'''
        
        result = []
        for hash, offset in hashes:
            result.append((hash, song_id, offset))
        
        with self.cursor as cur:
            for values in zip_lists(result, 1000):
                cur.executemany(self.INSERT_FINGERPRINT, values)
            
            
        
            
            
    def collect_matches(self, hashes):
        ''' Selects ()tuples '''
        dict = {}
        for hash, time_offset in hashes:
            dict[hash] = time_offset
        
        values = dict.keys()
        
        with self.cursor() as cur:
            for v in zip_lists(values, 1000):
                query = self.SELECT_MANY
                query = query % ',' .join(['UNHEX(%s)'] * len(v))
        
                cur.execute(query, v)
                
                
                for hash, song_id, t_delta in cur:
                    yield(song_id, t_delta - dict[hash] )
        
            
def setup_cursor(**resources):
    def cursor(**menu):
        menu.update(resources)
        return Cursor(**menu)
    return cursor

def zip_lists(iterable, n):
    pos = [iter(iterable)] * n
    return (filter(None, v) for v in zip_longest(*pos))
    
    
    
        
class Cursor(object):
    
    
    '''
    Establishes connection to the sql database
    '''
    
    
    def __init__(self, cursor_type = mysql.cursors.Cursor, **menu):

        super(Cursor, self).__init__()
        
        self.cache = queue.Queue(maxsize=5)
            
        try:
            conn = self.cache.get_nowait()
        except queue.Empty:
            conn = mysql.connect(**menu)
        else:
            conn.ping(True)
        
           
            
        self.conn = conn
        self.conn.autocommit(False)
        self.cursor_type = cursor_type
            
            
              
    def __enter__(self):
        self.cursor = self.conn.cursor(self.cursor_type)
        return self.cursor
            
    def __exit__(self, type, value, traceback):
        if type is mysql.MySQLError:
            self.cursor.rollback()
            
        self.cursor.close()
        self.conn.commit()
        
        # INSERT cursor back onto queue when connection to database is terminated 
        try:
            self.cache.put_nowait(self.conn)
        except queue.Full:
            self.conn.close()
        
        
        
        
        
        
        