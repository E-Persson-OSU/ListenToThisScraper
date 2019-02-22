#l2tscraperdb.py

import sqlite3

#Create DB if it doesn't exist
def initdb(rfp, logger):
    conn = sqlite3.connect(rfp)
    cur = conn.cursor()
    try:
        cur.execute('CREATE TABLE Tracks (id TEXT, title TEXT, artists TEXT, added INTEGER, popularity INTEGER)')
        logger.info('Table Created')
        conn.commit()
    except sqlite3.OperationalError as error:
        logger.error(error, exc_info=True)
    
    conn.close()

#Increments popularity field by 1 of given track ID
def raisepopularity(rfp, track_id, logger):
    conn = sqlite3.connect(rfp)
    cur = conn.cursor()
    try:
        cur.execute('UPDATE Tracks SET popularity WHERE id = ?',(track_id,))
        conn.commit()
        logger.info('{} popularity incremented.}'.format(track_id))
    except sqlite3.OperationalError as error:
        logger.error(error, exc_info=True)
    conn.close()

def addtrack(rfp, logger, id, added, title='Unknown',artists='Unknown',popularity=1):
    conn = sqlite3.connect(rfp)
    cur = conn.cursor()
    logger.info('Searching for record: {}'.format(id))
    cur.execute('SELECT id FROM Tracks WHERE id=?', (id,))
    entry = cur.fetchone()
    if entry is None:
        cur.execute('INSERT INTO Tracks (id, title, artists, added, popularity) VALUES (?,?,?,?,?);',
                        (id, title, artists, added, 1,))
        conn.commit()
        logger.info('Record Added.')
    else:
        raisepopularity(rfp, entry, logger)

    conn.close()

def checkfortrack(rfp, logger, id):
    conn = sqlite3.connect(rfp)
    cur = conn.cursor()
    cur.execute('SELECT id FROM Tracks WHERE id=?', (id,))
    record = cur.fetchone()
    conn.close()
    return record is not None

def getage(rfp, logger, id):
    age=0
    conn = sqlite3.connect(rfp)
    cur = conn.cursor()
    cur.execute('SELECT added FROM Tracks WHERE id=?', (id,))
    age = cur.fetchone()
    conn.close()
    return age