#L2TScraperSpotify.py

#Acquires Necessary Token for 
def spotipyconnect(user,scope,sci,scs,ruri):
    token = util.prompt_for_user_token(user,scope,sci,scs,ruri)
    return spotipy.Spotify(token),token

#Scrape ListenToThis

def scrapel2t(reddit):
    songs = []
    l2t = reddit.subreddit('listentothis')
    for submission in l2t.hot(limit=25):
        songs.append(submission.title)
    songs.pop(0)
    return songs

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
def addsongstoplaylist(playlist, token, spot): 
    spot.trace = False
    playlist = list(set(playlist))
    results = spot.user_playlist_add_tracks(su, spid, playlist)
    print(results)

#clear playlist before adding songs to avoid dupes
def emptyplaylist(spt, token, currenttracks):
    spt.user_playlist_remove_all_occurrences_of_tracks(su, spid, currenttracks)

#Check Spotify playlist
def checkplaylist(token):
    pl = []
    spt = spotipy.Spotify(auth=token)
    playlist = spt.user_playlist(su,spid)
    items = playlist['tracks']['items']
    for track in items:
        pl.append(track['track']['id'])
    return pl