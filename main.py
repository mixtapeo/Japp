import spotipy
import os
import requests
import json
from pprint import pprint 
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials


load_dotenv() #loads .env file

#gets virtualised credentials from .env file. replace with credentials if needed
client_id = os.getenv("client_id")  
client_secret = os.getenv("client_secret")
redirect_uri = 'http://localhost:8888/callback'

#spotipy credentials handlers
client_credentials_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(auth_manager=spotipy.SpotifyOAuth(scope='user-read-playback-state'))

#send request for user info. scope is important.
spotipy.prompt_for_user_token(username='', scope='user-read-playback-state', client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)

#storing info.
current_playing = sp.current_playback(market=None)

#print(f'FULLINFO STRING: {current_playing}')                       #Full server reply  
track_name = current_playing['item']['name']
track_time = current_playing['progress_ms']
track_time_s = track_time/1000                        #track time in seconds {DEPRECATED}

track_duration = (current_playing['item']['duration_ms'])/1000 #required parameters for fetch below
track_times = [str(track_time) + ' ms', str(track_time/1000) + ' seconds'] 
artist_name = current_playing['item']['artists'][0]['name']
album_name = current_playing['item']['album']['name']

#debug
print(f'track_duration (s): {track_duration}')
print(f'track_name: {track_name}')
print(f'artist_name: {artist_name}')
print(f'album_name: {album_name}')

def fetch(artist_name, track_name, album_name, track_duration):      #fetch timed lyrics from LRCLIB
    url = f'https://lrclib.net/api/get?artist_name={artist_name}&track_name={track_name}&album_name={album_name}&duration={track_duration}'
    response = requests.get(url)        
    try:
        lyrics = ((json.loads(response.text))['syncedLyrics'])
        pprint(lyrics)
    except:
        print(f'{(json.loads(response.text))['message']}, Reason: {(json.loads(response.text))["name"]}, Code: {(json.loads(response.text))["statusCode"]}')

fetch(artist_name, track_name, album_name, track_duration)