# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task, task

from .models import SpotifyInfo, Song, Voter, VotedSong

from django.db.models import Count

from . import spot

import random

def is_next_song(si):
    
    c = si.currently_playing(spot)
    if c is None:
        return False
    t = si.get_progress()
    tot = c.duration_ms
    if tot - t < 30000: # 30 seconds
        # song is locked in
        if c.song_id != si.last_locked_in_id:
            
            si.last_locked_in_id = c.song_id
            si.save()

            return True
        else:
            print('already locked in')
            return False
        return True
    return False


def set_next_song(si):
    songs = Song.objects.annotate(votes=Count('voter')).order_by('-votes')
    max_votes = songs[0].votes
    # Make sure a song was chosen
    if max_votes == 0:
         # Choose a song from default playlist
         items = spot.get_playlist_tracks(si, pid=si.default_playlist)['items']
         if si.playlist_index >= len(items):
            # End of playlist has been reached, loop to the beginning again
            si.playlist_index = 0
            si.save() 
         s_info = items[si.playlist_index]['track']
         song = Song(song_id=s_info['id'],
            song_name=s_info['name'],
            artist=', '.join(a['name'] for a in s_info['artists']),
            artwork=s_info['album']['images'][0]['url'],
            duration_ms=s_info['duration_ms'],
            queued=True)
         song.save()
         # Increment playlist index
         si.playlist_index += 1
         si.save()
    else:
        # Find top song from songs voted on
        top_songs = songs.filter(votes=max_votes)
        # Choose randomly for case when there are more than one
        song = random.choice(list(top_songs))
        # queue song
        song.queued = True
        song.save()


    # Add track to track history in database
    vs = VotedSong(song_id=song.song_id, song_name=song.song_name, artist=song.artist, artwork=song.artwork)
    vs.save()
    # transfer over voters
    for voter in Voter.objects.filter(vote=song):
        voter.past_votes.add(vs)
        voter.vote = None
        voter.save()

    # Actually queue song on spotify
    spot.add_track(si, song.song_id)



@task
def my_task(*args):
    si = SpotifyInfo.objects.all()[0]
    if not si.running:
        return
    print('checking...')
    # Get current song
    if is_next_song(si):
        print('locked in')
        try:
            print('setting next song')
            set_next_song(si)
            # r = requests.get(url+'/dj/next')
            # if r.status_code == 200:
            #     song = r.json()['song']
            #     # Actually queue song
            #     spot.add_track(song)
            # else:
            #     print('error communicating with server')
        except Exception as e:
            print('error communicating with server')
            print(e)
            return
