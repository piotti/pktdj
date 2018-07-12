from __future__ import print_function

import requests
import time

# from .models import SpotifyInfo


playlist_id='6UldUApuGGIUvoa0SwLTUM'
scope = 'user-read-private user-read-email playlist-read-private playlist-modify-private user-read-playback-state user-modify-playback-state user-read-currently-playing user-read-recently-played'
username = '1234397309'

def get_token(si):
    global token

    # si = SpotifyInfo.objects.all()[0]
    token = si.token
    exp_time = si.time
    if exp_time <= time.time() + 60:
        print('refreshing token')
        refresh_token(si)


def refresh_token(si):
    global token
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': si.refresh_token,
        'client_id':si.client_id,
        'client_secret':si.client_secret,
    }
    r = requests.post('https://accounts.spotify.com/api/token', data=data)
    if r.status_code != 200:
        print( 'couldnt refresh token')
        print( r.json())
        return
    token = r.json()['access_token']
    # save new token
    # si = SpotifyInfo.objects.all()[0]
    si.token = token
    si.time = time.time() + 3600
    si.save()

def api_get(si, url, **params):
    get_token(si)
    return requests.get('https://api.spotify.com/v1/'+url, params=params, headers={'Authorization': 'Bearer '+str(token)}).json()

def api_post(si, url, data=None, **params):
    get_token(si)
    return requests.post('https://api.spotify.com/v1/'+url, data=data, params=params, headers={'Authorization': 'Bearer '+str(token)}).json()
def api_delete(si, url, data):
    get_token(si)
    import json
    return requests.delete('https://api.spotify.com/v1/'+url, data=json.dumps(data), headers={'Authorization': 'Bearer '+str(token), 'Content-Type': 'application/json'}).json()

def currently_playing(si):
    return api_get(si, 'me/player/currently-playing')

def add_track(si, song):
    return api_post(si, 'users/%s/playlists/%s/tracks' % (username, playlist_id), uris='spotify:track:'+song)

def get_playlist_tracks(si, pid=playlist_id):
    return api_get(si, 'users/%s/playlists/%s/tracks' % (username, pid))

def remove_playlist_tracks(si, songs):
    data = {'tracks': songs}
    print(data)
    return api_delete(si, 'users/%s/playlists/%s/tracks' % (username, playlist_id), data)
