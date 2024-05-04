from fnmatch import translate
import spotipy
import os
import requests
import json
import re
from pprint import pprint 
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials
from deep_translator import GoogleTranslator


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

def fetch(artist_name, track_name, album_name, track_duration):     #fetch lyrics from LRCLIB
    url = f'https://lrclib.net/api/get?artist_name={artist_name}&track_name={track_name}&album_name={album_name}&duration={track_duration}'
    server_response = requests.get(url) 
    response = ((json.loads(server_response.text))['syncedLyrics']) #use syncedLyrics instead of plainLyrics for timed lyrics.
    return response

def parse_lyrics(response): #storing timestamp and lyric text as a dictionary
    lyrics_dict = {}
    lines = response.strip().split('\n')
    
    for line in lines:
        match = re.match(r'\[(\d+:\d+\.\d+)\]\s*(.*)', line)
        if match:
            timestamp = match.group(1)
            lyric = match.group(2)
            lyrics_dict[timestamp] = lyric.strip()

    return lyrics_dict


response = fetch(artist_name, track_name, album_name, track_duration) #Fetch request
lyrics_dict = parse_lyrics(response) #Store timestamp and lyric text into dict


lyrics_text = []
for lyric in lyrics_dict.values(): #lyrics text in a list
    lyrics_text.append(lyric)

#DeepL translation
translated = []
i=0

for line in lyrics_text: #translated text into a dictionary
    i+=1
    if line == '':
        pass
    else:
        translated_line = GoogleTranslator(source='auto', target='en').translate(line)
        print(f'{i}: "{translated_line}"')
        translated.append(translated_line)

print(translated)