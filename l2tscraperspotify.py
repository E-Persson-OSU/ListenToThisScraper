#L2TScraperSpotify.py

#imports
import spotipy
from spotipy import util



#Acquires Necessary Token for specified scope
#Requires user=<Spotify Username>, sci=<Spotify Client ID>, ruri=<Redirect URI>, scope=<'playlist-modify-public'>
def spotipyconnect(user,sci,scs,ruri,scope='playlist-modify-public'):
    token = util.prompt_for_user_token(user,scope,sci,scs,redirect_uri=ruri)
    return spotipy.Spotify(token),token

def convertospotify(songstoadd,token):
    spt = spotipy.Spotify(auth=token)
    spotifysonglist = []
    for song in songstoadd:
        try:
            try:
                result = spt.search(q=str(song).split('-')[1].split(' [')[0], limit=1, type='track')
            except spotipy.client.SpotifyException as spte:
                print(str(spte))
        except IndexError as ie:
            print(str(ie))
        try:
            spotifysonglist.append(result['tracks']['items'][0]['id'])
        except IndexError as ie:
            print(str(ie))
    return spotifysonglist
        

#Add Songs to Spotify Playlist
def addsongstoplaylist(playlist, token, spot, spotifyusername, spotifyplaylistid ): 
    spot.trace = False
    playlist = list(set(playlist))
    results = spot.user_playlist_add_tracks(spotifyusername, spotifyplaylistid, playlist)
    print(results)

#clear playlist before adding songs to avoid dupes
def emptyplaylist(spt, token, currenttracks, spotifyusername, spotifyplaylistid):
    spt.user_playlist_remove_all_occurrences_of_tracks(spotifyusername, spotifyplaylistid, currenttracks)

#Check Spotify playlist
def checkplaylist(token, spotifyusername, spotifyplaylistid):
    pl = []
    spt = spotipy.Spotify(auth=token)
    playlist = spt.user_playlist(spotifyusername,spotifyplaylistid)
    items = playlist['tracks']['items']
    for track in items:
        pl.append(track['track']['id'])
    return pl