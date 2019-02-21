#l2tscraperdb.py

import sqlite3

#Create DB if it doesn't exist
def initdb(rfp, logger):
    conn = sqlite3.connect(rfp)
    cur = conn.cursor()
    try:
        cur.execute('CREATE TABLE Tracks (id TEXT, title TEXT, artists TEXT, added INTEGER, popularity INTEGER)')
        logger.info('Table Created')
    except sqlite3.OperationalError as error:
        logger.error(error, exc_info=True)
    
    conn.close()

#Increments popularity field by 1 of given track ID
def raisepopularity(rfp, track_id, logger):
    conn = sqlite3.connect(rfp)
    cur = conn.cursor()
    try:
        cur.execute('UPDATE Tracks SET popularity WHERE id = ?',(track_id,))
        logger.info('{} popularity incremented.}'.format(track_id))
    except sqlite3.OperationalError as error:
        logger.error(error, exc_info=True)
