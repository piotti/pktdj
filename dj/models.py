from django.db import models
import traceback

import time



# Create your models here.

class Feedback(models.Model):
    name = models.CharField(max_length=128, blank=True)
    feedback = models.TextField(blank=True)
    time = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name


class Song(models.Model):
    song_id = models.CharField(max_length=64)
    song_name = models.CharField(max_length=64)
    artist = models.CharField(max_length=64)
    queued = models.BooleanField(default=False)
    artwork = models.CharField(max_length=256, blank=True)
    duration_ms = models.IntegerField(default=0)
    dj_pick = models.BooleanField(default=False)

    def __str__(self):
        return self.song_name + ' - ' + self.artist



class Voter(models.Model):
    ip = models.CharField(max_length=128)
    vote = models.ForeignKey(Song, on_delete=models.SET_NULL, null=True, blank=True)


    def __str__(self):
        return self.ip



class SpotifyInfo(models.Model):
    token = models.CharField(max_length=256)
    time = models.FloatField()

    running = models.BooleanField(default=False)

    last_play_time = models.FloatField(default=0)
    playing = models.OneToOneField(Song, null=True, blank=True, on_delete=models.SET_NULL)
    progress_ms = models.IntegerField(default=0)

    last_locked_in_id = models.CharField(blank=True, max_length=256, null=True)

    playlist_index = models.PositiveIntegerField(default=0)

    client_id = models.CharField(max_length=64, blank=True)
    client_secret = models.CharField(max_length=64, blank=True)
    refresh_token = models.CharField(max_length=256, blank=True)
    default_playlist = models.CharField(max_length=64, blank=True)
    

    def get_progress(self):
        return self.progress_ms + (time.time()-self.last_play_time)*1000

    def currently_playing(self, spot):
        if not self.running:
            return None
        if time.time() - self.last_play_time > 2 or self.playing is None:
            print('resetting')
            try:
                r = spot.currently_playing(self)
            except Exception as e:
                print('error')
                traceback.print_exc()
                return None

            if Song.objects.filter(song_id=r['item']['id']):
                # song already exists, set playing to this song
                s = Song.objects.get(song_id=r['item']['id'])
                s.queued = False
                s.save()
                self.playing = s

            else:
                # Create new song object
                s = Song(song_id=r['item']['id'],
                    song_name=r['item']['name'],
                    artist=', '.join(a['name'] for a in r['item']['artists']),
                    artwork=r['item']['album']['images'][0]['url'],
                    duration_ms=r['item']['duration_ms'])
                self.playing = s
                s.save()

            # update time
            self.last_play_time = time.time()
            self.progress_ms = r['progress_ms']
            
            self.save()
        
        return self.playing











