from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse, Http404, JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.contrib import auth
from django.contrib.auth.decorators import login_required

from django.db.models import Count

import random

import time

from . import spot

from .models import Song, Voter, SpotifyInfo, Feedback





# Create your views here.

def index(request):
    # d = {'songs': Song.objects.all()}
    return render(request, 'dj/index.html')

def format_time(ms):
    seconds = int(ms / 1000)
    minutes = int(seconds / 60)
    seconds = seconds % 60

    return str(minutes) + ':' + str(seconds)



def info(request):
    si = SpotifyInfo.objects.all()[0]
    curr_song = si.currently_playing(spot)
    if curr_song is None:
        # app is basically off
        return JsonResponse({'on': False}, safe=False)

    curr_id = curr_song.song_id
    current = {
        'name': curr_song.song_name,
        'artists': curr_song.artist,
        'id': curr_song.song_id,
        'time': si.get_progress(),
        'duration': curr_song.duration_ms,
        'artwork': curr_song.artwork,
    }
    queued = Song.objects.filter(queued=True).exclude(song_id=curr_id)
    if queued:
        queued = queued[0]
        if current['duration'] - current['time'] > 30000: # 30 seconds
            # don't display
            queued = 'None'
        else:
            queued = {
                'name': queued.song_name,
                'artists': queued.artist,
                'artwork': queued.artwork,

            }
    else:
        queued = 'None'
    songs = Song.objects.annotate(votes=Count('voter')).order_by('-votes').exclude(queued=True).exclude(song_id=curr_id).filter(votes__gte=1)[:5]
    q = [ {
        'name': e.song_name,
        'artists': e.artist,
        'votes': e.votes,
        'song_id':e.song_id,
        'artwork':e.artwork
        } for e in songs]

    d = {
        'on': True,
        'current': current,
        'queued': queued,
        'voting': q,
    }

    return JsonResponse(d, safe=False)



def search(request):
    si = SpotifyInfo.objects.all()[0]
    q = request.GET['q']
    results = spot.api_get(si, 'search', q=q, limit=10, offset=0, type='track')

    songs = []
    for item in results['tracks']['items']:
        d = {
            'name': item['name'],
            'artists': ', '.join(a['name'] for a in item['artists']),
            'album': item['album']['name'],
            'time': format_time(item['duration_ms']),
            'id': item['id'],
        }
        songs.append(d)
    

    # formatted = [names[i] + '   -   ' + artists[i] for i in range(len(songs))]

    return JsonResponse({'songs': songs}, safe=False)


def vote(request, song_id):
    si = SpotifyInfo.objects.all()[0]
    # Get ip
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    # Check if song already getting voted on
    song = Song.objects.filter(song_id=song_id)
    if not song:
        # Add new song
        # sp = spot.start()
        result = spot.api_get(si, 'tracks/'+song_id)
        song = Song(song_id=song_id,
            song_name=result['name'],
            artist=', '.join(a['name'] for a in result['artists']),
            artwork=result['album']['images'][0]['url'],
            duration_ms=result['duration_ms'])
        song.save()
    else:
        song = song[0]
        # Check that song isn't currently playing
        if song == si.currently_playing(spot):
            return JsonResponse({'result': 'error: song currently playing'}, safe=False)

    # Check if user exists
    user = Voter.objects.filter(ip=ip)
    if not user:
        # Create user
        user = Voter(ip=ip, vote=song)
        user.save()
    else:
        user = user[0]
        user.vote = song
        user.save()

    return JsonResponse({'result': 'success'}, safe=False)

def feedback(request):
    return render(request, 'dj/feedback.html', {'submitted': request.GET.get('submitted', False)})

@csrf_protect
def feedback_submit(request):
    
    name = request.POST.get('name', '')
    feedback = request.POST.get('feedback', str(request.POST))
    if name == '' and feedback == '':
        return redirect(reverse('dj:feedback'))

    fb = Feedback(name=name, feedback=feedback)
    fb.save()


    return redirect(reverse('dj:feedback') + '?submitted=true')


def admin(request):
    # Get what could be the next song
    si = SpotifyInfo.objects.all()[0]
    ind = si.playlist_index
    items = spot.get_playlist_tracks(si, pid=si.default_playlist)['items']
    if si.playlist_index >= len(items):
        # End of playlist has been reached, loop to the beginning again
        ind = 0
    s_info = items[si.playlist_index]['track']

    return render(request, 'dj/admin.html', {'invalid':request.GET.get('invalid', False),
        'logged_in':request.user.is_authenticated,
        'index': ind,
        'next': s_info['name'] + ' - ' + ', '.join(a['name'] for a in s_info['artists'])
        })


@csrf_protect
def login(request):

    username = request.POST['username']
    pw = request.POST['pw']
    user = auth.authenticate(username=username, password=pw)
    if user is not None:
        auth.login(request, user)
    else:
        return redirect(reverse('dj:admin')+'?invalid=true')

    return redirect(reverse('dj:admin'))

@csrf_protect
def logout(request):

    auth.logout(request)
    return redirect(reverse('dj:admin'))



def reset_db(stop=False):
    Song.objects.all().delete()
    Voter.objects.all().delete()
    si = SpotifyInfo.objects.all()[0]
    si.last_locked_in_id = None
    si.last_play_time = 0
    si.playing = None
    si.progress_ms = 0
    if stop:
        si.running = False
    si.save()


@login_required
def setindex(request):
    si =  SpotifyInfo.objects.all()[0]
    si.playlist_index = request.POST['index']
    si.save()
    return redirect(reverse('dj:admin'))


@login_required
def reset(request):

    reset_db()

    return JsonResponse({'msg': 'reset db'}, safe=False)

@login_required
def start(request):
    si =  SpotifyInfo.objects.all()[0]
    if si.running:
        return JsonResponse({'msg': 'already running'}, safe=False)

    si.running = True
    si.save() 

    return JsonResponse({'msg': 'process started'}, safe=False)

@login_required
def stop(request):
    si =  SpotifyInfo.objects.all()[0]
    if not si.running:
        return JsonResponse({'msg': 'already stopped'}, safe=False)

    reset_db(stop=True)

    return JsonResponse({'msg': 'process stopped'}, safe=False)

