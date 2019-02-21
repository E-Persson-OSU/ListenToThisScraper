#l2tscraperdb.py

import sqlite3

#Create DB if it doesn't exist
def initdb(rfp):
    conn = sqlite3.connect(rfp)
    cur = conn.cursor()
    try:
        cur.execute('CREATE TABLE Tracks (id TEXT, added INTEGER)')
    except sqlite3.OperationalError as error:
        print(error)
    
    conn.close()