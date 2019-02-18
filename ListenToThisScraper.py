#ListenToThisScraper.py

#imports
import praw
import sqlite3
import spotipy
import spotipy.util as util
import time
import os
import http.server
import socketserver
from configparser import ConfigParser

#Flow
#connect to praw and spotify
#connect to database
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
rp = cfg['reddit']['password']           #Reddit Password
ru = cfg['reddit']['username']           #Reddit Username

#Spotify Info
sci = cfg['spotify']['client_id']       #Spotify Client ID
scs = cfg['spotify']['client_secret']   #Spotify Client Secret
sp = cfg['spotify']['password']         #Spotify Password
su = cfg['spotify']['username']         #Spotify Username
st = cfg['spotify']['token']            #Spotify Token
spid = cfg['spotify']['playlist_id']    #Spotify Playlist ID
scope = 'playlist-modify-public'
redirect_uri = cfg['spotify']['redirect_uri']

#Running Info
rfp = cfg['files']['removed_songs']     #Removed Songs File Path


#-----------Private Functions-----------------

#PRAW connect


def prawconnect():
    return praw.Reddit(client_id=rci,
                     client_secret=rcs,
                     user_agent='l2tbot user agent')

#Spotipy connect

def spotipyconnect(user,scope,sci,scs):
    token = util.prompt_for_user_token(user,scope,sci,scs,redirect_uri)
    return spotipy.Spotify(token),token

#Scrape ListenToThis

def scrapel2t(reddit):
    songs = []
    l2t = reddit.subreddit('listentothis')
    for submission in l2t.hot(limit=25):
        songs.append(submission.title)
    return songs

def convertospotify(songstoadd,token):
    spt = spotipy.Spotify(auth=token)
    for song in songstoadd:
        



#Check Spotify playlist
def checkplaylist(token):
    pl = []
    spt = spotipy.Spotify(auth=token)
    playlist = spt.user_playlist(su,spid)
    items = playlist['tracks']['items']
    for track in items:
        pl.append(track['track']['id'])
    return pl
    
#Compare currentsongs and addsongs to database, if old remove, compile both lists into one list
def comparecurrent(currentsongs, addsongs):
    conn = sqlite3.connect(rfp)
    cur = conn.cursor() 
    addtime = time.time()
    for id in currentsongs:
        try:
            cur.execute('SELECT id FROM Tracks WHERE id=?', (id,))
        except sqlite3.OperationalError:
            cur.execute('INSERT INTO Tracks (id, added) VALUES (?,?);', (id, time.time(),))
    for id in addsongs:
        try:
            cur.execute('SELECT id FROM Tracks WHERE id=?', (id,))
        except sqlite3.OperationalError:
            cur.execute('INSERT INTO Tracks (id, added) VALUES (?,?);', (id, time.time(),))
    conn.close()
    return songstoremove

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



#Create DB if it doesn't exist
def initdb():
    conn = sqlite3.connect(rfp)
    cur = conn.cursor()
    try:
        cur.execute('CREATE TABLE Tracks (id TEXT, added INTEGER)')
    except sqlite3.OperationalError as error:
        print(error)
    
    conn.close()

#end

#-----------Main Method-----------------
def main():
    #startserver()
    initdb()
    while(True):
        reddit = prawconnect()
        spt,token = spotipyconnect(su, scope, sci, scs)
        removedsongfilecheck(rfp)
        addsongs = scrapel2t(reddit)
        addsongs = convertospotify(addsongs)
        addsongs = removedsongs(addsongs)
        currentsongs = checkplaylist(token)
        #TODO check database for songs to remove and remove
        songstoremove = comparecurrent(currentsongs,addsongs)

        #TODO add songs to playlist
        
        time.sleep(86400) #sleep for one day
        



if __name__ == "__main__":
    main()

