#ListenToThisScraper.py

import http.server
import os
import socketserver
import sqlite3
import time
from configparser import ConfigParser

#imports
import praw
import spotipy
import spotipy.util as util
import Scripts.l2tscraperspotify

#Flow
#connect to praw and spotify
#connect to databases
#Scrape Reddit r/ListenToThis, save as 'addsongs'
#Compare 'addsongs' to database
    #if already in database, remove and increment popularity on that song in database
#Pull songs from spotify playlist, save as 'currentsongs'
#compare 'currentsongs' to database
    #if date in 'Added' field is over a week ago, remove song from currentsongs, add to 'removedsongs'
    #else add song to database with fields 'id' and 'Added'
#Compare removedsongs and addsongs
    #if any removedsongs == addsongs, remove from addsongs
#Add addsongs to playlist
#wait for one day

#-------------globalvariables-----------------

playlist = 'https://open.spotify.com/playlist/0R2kxFWpcaUn6vrmKWZSSY'

addsongs = []

#configparser setup
cfg = ConfigParser()
cfg.read('bot.ini')

#Reddit Info
rci = cfg['reddit']['client_id']         #Reddit Client ID
rcs = cfg['reddit']['client_secret']     #Reddit Secret

#Spotify Info
sci = cfg['spotify']['client_id']        #Spotify Client ID
scs = cfg['spotify']['client_secret']    #Spotify Client Secret
spid = cfg['spotify']['playlist_id']     #Spotify Playlist ID
su = cfg['spotify']['username'] 
scope = 'playlist-modify-public'
redirect_uri = cfg['spotify']['redirect_uri']

#Running Info
rfp = cfg['files']['removed_songsfp']      #Removed Songs File Path


#-----------Private Functions-----------------
        

    
#Compare currentsongs and addsongs to database, if old remove, compile both lists into one list
    #currentsongs over the time limit need to be removed, addsongs need to be checked against the database for duplicates and removed
def comparecurrent(currentsongs, addsongs):
    conn = sqlite3.connect(rfp)
    cur = conn.cursor() 
    addtime = time.time()
    added = 'Initial Value'
    #remove addsongs from currentsongs, might do something else with them later
    for id in addsongs:
        try:
            currentsongs.remove(id)
        except ValueError as ve:
            print(id + ' not found in current songs.')
    
    #back to the script
    for id in currentsongs:
        try:
            cur.execute('SELECT added FROM Tracks WHERE id=?', (id,))
            added = cur.fetchone()
            if added == None:
                print('No time found for ' + id)
            elif int(addtime) - int(added) > 604800:
                currentsongs.remove(id)
        except sqlite3.OperationalError:
            cur.execute('INSERT INTO Tracks (id, added) VALUES (?,?);', (id, time.time(),))
    for id in addsongs:
        try:
            check = cur.execute('SELECT id FROM Tracks WHERE id=?', (id,))
            if check == id:
                addsongs.remove(id)
        except sqlite3.OperationalError:
            cur.execute('INSERT INTO Tracks (id, added) VALUES (?,?);', (id, time.time(),))
    conn.close()
    for id in addsongs:
        currentsongs.append(id)
    return currentsongs

#check list of removed songs
#TODO make this check against database instead of text file
def removedsongs(songstoadd):
    newsongs = []
    with open(rfp, 'r') as removed:
        for song in songstoadd:
            if song not in removed:
                newsongs.append(song)
    return newsongs

def removedsongfilecheck(path):
    try:
        fp = open(path)
    except IOError:
        fp = open(path, 'w+')


#end

#-----------Main Method-----------------
def main():
    initdb()
    while(True):
        reddit = prawconnect()
        spt,token = spotipyconnect(su, scope, sci, scs)
        removedsongfilecheck(rfp)
        addsongs = scrapel2t(reddit)
        addsongs = convertospotify(addsongs,token)
        addsongs = removedsongs(addsongs)
        currentsongs = checkplaylist(token)
        emptyplaylist(spt, token, currentsongs)
        newplaylist = comparecurrent(currentsongs,addsongs)
        addsongstoplaylist(newplaylist, token, spt)
        
        time.sleep(86400) #sleep for one day
        



if __name__ == "__main__":
    main()
