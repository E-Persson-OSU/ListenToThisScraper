# L2TScraperSpotify.py

# imports
import spotipy
from spotipy import util


# Acquires Necessary Token for specified scope
# Requires user=<Spotify Username>, sci=<Spotify Client ID>, ruri=<Redirect URI>, scope=<'playlist-modify-public'>
def spotipyconnect(user, sci, scs, ruri, scope='playlist-modify-public'):
    token = util.prompt_for_user_token(
        user, scope, sci, scs, redirect_uri=ruri)
    return spotipy.Spotify(token), token


def convertospotify(songstoadd, token, names_and_ids, logger):
    spt = spotipy.Spotify(auth=token)
    result = 'Oops'
    for song in songstoadd:
        errored = False
        try:
            try:
                result = spt.search(q=str(song).split(
                    '-')[1].split(' [')[0], limit=1, type='track')
            except spotipy.client.SpotifyException as spte:
                logger.error(str(spte), exc_info=True)
                errored = True
        except IndexError as ie:
            logger.error(str(ie), exc_info=True)
            errored = True
        if not errored:
            try:
                id = result['tracks']['items'][0]['id']
                artistlist = ''
                name = result['tracks']['items'][0]['name']
                for artist in result['tracks']['items'][0]['artists']:
                    artistlist = artistlist + ' ' + artist['name']

                logger.info('ID: {}, Title: {}, Artist(s): {}'.format(
                    id, name, artistlist))
                names_and_ids[id] = (name, artistlist)

            except IndexError as ie:
                logger.error(str(ie), exc_info=True)
    return names_and_ids


# Add Songs to Spotify Playlist
def addsongstoplaylist(playlist, token, spot, spotifyusername, spotifyplaylistid, logger):
    logger.info('Adding songs to playlist')
    spot.trace = False
    logger.info('Removing duplicates')
    playlist = list(set(playlist))
    results = spot.user_playlist_add_tracks(
        spotifyusername, spotifyplaylistid, playlist)
    logger.debug(results)

# clear playlist before adding songs to avoid dupes


def emptyplaylist(spt, token, currenttracks, spotifyusername, spotifyplaylistid, logger):
    logger.info('Clearing Playlist')
    spt.user_playlist_remove_all_occurrences_of_tracks(
        spotifyusername, spotifyplaylistid, currenttracks)

# Check Spotify playlist


def checkplaylist(token, spotifyusername, spotifyplaylistid, logger):
    logger.info('Checking Playlist')
    pl = []
    spt = spotipy.Spotify(auth=token)
    playlist = spt.user_playlist(spotifyusername, spotifyplaylistid)
    items = playlist['tracks']['items']
    for track in items:
        pl.append(track['track']['id'])
    return pl
