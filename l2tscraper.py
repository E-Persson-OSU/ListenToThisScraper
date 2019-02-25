# ListenToThisScraper.py
import praw
from l2tscraperspotify import (addsongstoplaylist, checkplaylist,
                               convertospotify, emptyplaylist, spotipyconnect)
from l2tscraperdb import initdb, raisepopularity, checkfortrack, addtrack, getage
from configparser import ConfigParser
import time
import sqlite3
import socketserver
import os
import http.server
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
handler = logging.FileHandler('l2t.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

logger.info('Loading Imports')

# Flow
# connect to praw and spotify
# connect to databases
# Scrape Reddit r/ListenToThis, save as 'addsongs'
# Compare 'addsongs' to database
# if already in database, remove and increment popularity on that song in database
# Pull songs from spotify playlist, save as 'currentsongs'
# compare 'currentsongs' to database
# if date in 'Added' field is over a week ago, remove song from currentsongs, add to 'removedsongs'
# else add song to database with fields 'id' and 'Added'
# Compare removedsongs and addsongs
# if any removedsongs == addsongs, remove from addsongs
# Add addsongs to playlist
# wait for one day

# -------------globalvariables-----------------

logger.info('Loading bot.ini')
playlist = 'https://open.spotify.com/playlist/0R2kxFWpcaUn6vrmKWZSSY'

addsongs = []
namedict = dict()

# configparser setup
cfg = ConfigParser()
cfg.read('bot.ini')

# Reddit Info
rci = cfg['reddit']['client_id']  # Reddit Client ID
rcs = cfg['reddit']['client_secret']  # Reddit Secret
ru = cfg['reddit']['username']  # Reddit Username
rp = cfg['reddit']['password']  # Reddit Password

# Spotify Info
sci = cfg['spotify']['client_id']  # Spotify Client ID
scs = cfg['spotify']['client_secret']  # Spotify Client Secret
spid = cfg['spotify']['playlist_id']  # Spotify Playlist ID
su = cfg['spotify']['username']
scope = 'playlist-modify-public'
redirect_uri = cfg['spotify']['redirect_uri']

# Running Info
rfp = cfg['files']['removed_songsfp']  # Removed Songs File Path


# -----------Private Functions-----------------


logger.info('Loading functions')

# Scrapes l2t with option to upvote, takes considerably longer.


def scrapel2t(reddit, upvote):
    logger.info('Scraping /r/ListenToThis')
    songs = []
    l2t = reddit.subreddit('listentothis')
    for submission in l2t.hot(limit=100):
        logger.info('Scraped ' + submission.title)
        songs.append(submission.title)
        if upvote == 'y':
            logger.info('Upvoting submission')
            submission.upvote()
    return songs


def compareandadd(spotifyplaylistsongs, l2tsongs):
    logger.info('Creating cursor')
    addtime = time.time()
    logger.info('Time added')
    added = 'Initial Value'

    repeatedsongs = list()
    for id in l2tsongs:
        try:
            repeatedsongs.append(spotifyplaylistsongs.remove(id))
        except ValueError as ve:
            logger.info(id + ' not found in current songs.')

    lessthanweekold = list()
    for id in l2tsongs.keys():
        logger.info('Checking if {} exists.'.format(id))
        exists = checkfortrack(rfp, logger, id)
        logger.info('Exists? {}'.format(exists))
        if not exists:
            trackdetails = l2tsongs[id]
            title = trackdetails[0]
            artists = trackdetails[1]
            logger.debug('{} {} {}'.format(id, title, artists))
            addtrack(rfp, logger, id, addtime, title, artists)
            logger.info('Added entry.')
            lessthanweekold.append(id)
        else:
            logger.info('Raising popularity')
            raisepopularity(rfp, id, logger)
            agedb = getage(rfp, logger, id)
            underweek = int(addtime - agedb) < 604800
            logger.debug('{} under a week old? {}'.format(id, underweek))
            if underweek:
                lessthanweekold.append(id)

    logger.info('Checking Spotify Songs')
    for id in spotifyplaylistsongs:
        exists = checkfortrack(rfp, logger, id)
        logger.debug('{}? {}'.format(id, exists))
        if not exists:
            addtrack(rfp, logger, id, addtime)
            logger.info('Track added to database')
            lessthanweekold.append(id)
        else:
            agedb = getage(rfp, logger, id)
            underweek = int(addtime - agedb) < 604800
            logger.debug('{} under a week old? {}'.format(id, underweek))
            if underweek:
                lessthanweekold.append(id)

    return lessthanweekold


def removedsongfilecheck(path):
    try:
        fp = open(path)
        logger.info('Database exists.')
    except IOError:
        fp = open(path, 'w+')
        logger.info('Database did not exist, database created.')


# end

# -----------Main Method-----------------
def main():
    logger.info('Start Database')
    initdb(rfp, logger)
    startsleep = time.time()
    wait = True
    logger.debug('Time recorded: ' + str(startsleep))
    while(wait):
        namedict = dict()

        logger.info('Connecting to Reddit')
        logger.debug(
            'Reddit Client ID: {} Reddit_Client Secret: {}'.format(rci, rcs))
        reddit = praw.Reddit(client_id=rci, client_secret=rcs, password=rp,
                             username=ru, user_agent='l2tscraper by /u/ascendex')

        logger.info('Connecting to Spotify')
        spt, token = spotipyconnect(su, sci, scs, redirect_uri)
        logger.debug('Spotify token: {}'.format(token))

        logger.info('Checking if Database exists')
        removedsongfilecheck(rfp)

        logger.info('Prompt user for input')
        upvote = input('Upvote?[y/n]')
        logger.debug('User chose: {}'.format(upvote))
        logger.debug('Contents of addsongs:')
        addsongs = scrapel2t(reddit, upvote)
        namedict = convertospotify(addsongs, token, namedict, logger)

        tids = list(namedict.keys())
        for song in tids:
            raisepopularity(rfp, song, logger)
        logger.info('Compiling final list')

        currentsongs = checkplaylist(token, su, spid, logger)
        emptyplaylist(spt, token, currentsongs, su, spid, logger)
        newplaylist = compareandadd(currentsongs, namedict)
        addsongstoplaylist(newplaylist, token, spt, su, spid, logger)
        if wait:
            logger.info('Waiting until {}.'.format(
                time.ctime(time.time()+86400)))
            time.sleep(86400)


logger.info('Checking if __main__')
if __name__ == "__main__":
    logger.info('Execute main()')
    main()
