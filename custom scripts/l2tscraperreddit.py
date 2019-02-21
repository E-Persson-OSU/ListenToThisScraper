#l2tscraperreddit.py

import praw

#PRAW connect
def prawconnect():
    return praw.Reddit(client_id=rci,
                     client_secret=rcs,
                     user_agent='l2tbot user agent')

def scrapel2t(reddit):
    songs = []
    l2t = reddit.subreddit('listentothis')
    for submission in l2t.hot(limit=100):
        songs.append(submission.title)
    songs.pop(0)
    return songs