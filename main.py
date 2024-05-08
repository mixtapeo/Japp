import spotipy
import os
import requests
import json
import re
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials
from deep_translator import GoogleTranslator
from pprint import pprint
import customtkinter

load_dotenv() #loads .env file: gets virtuaDlised credentials from .env file. replace with credentials if needed

client_id = os.getenv("client_id")
client_secret = os.getenv("client_secret")
redirect_uri = 'http://localhost:8888/callback'

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

root = customtkinter.CTk()
root.geometry("1000x700")

root.title("Japp")

frame = customtkinter.CTkFrame(master=root)
frame.pack(pady = 0, padx = 0, fill = "both", expand = True)

textbox = customtkinter.CTkTextbox(master=frame, height=200, width = 3000, corner_radius=10)
textbox.place(relx=0.5, rely=0.5, relwidth=1, relheight=1, anchor="center")
textbox.pack(pady = 5, padx = 10)

textbox_2 = customtkinter.CTkTextbox(master=frame, height=200, width = 3000, corner_radius=10)
textbox_2.pack(pady = 5, padx = 10)

error_box = customtkinter.CTkLabel(master=frame, width=10, corner_radius=100, text = '')
error_box.pack(pady = 5, padx = 10)

button = customtkinter.CTkButton(master = frame, text = "Click to update...")
button.pack(pady = 5, padx = 15)

current_playing_box = customtkinter.CTkLabel(master=root, width=1, corner_radius=10)
current_playing_box.pack()

info_label = customtkinter.CTkLabel(master=root, width=2, corner_radius=0, text = "by @mixtapeo, 2024.")
info_label.pack()

#Functions
def spotify_request():
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

    track_duration = int(current_playing['item']['duration_ms'])/1000 #required parameters for fetch below
    track_times = f'{str(track_time)} ms', f'{str(track_time / 1000)} seconds'
    artist_name = current_playing['item']['artists'][0]['name']
    album_name = current_playing['item']['album']['name']

    #debug
    print(f'track_duration (s): {track_duration}')
    print(f'track_name: {track_name}')
    print(f'artist_name: {artist_name}')
    print(f'album_name: {album_name}')
    
    return track_name, artist_name, album_name, track_duration

def fetch(track_name, artist_name , album_name, track_duration):
    global status
    status = -1
    
    url = f'https://lrclib.net/api/get?artist_name={artist_name}&track_name={track_name}&album_name={album_name}&duration={track_duration}'
    print('FETCH STARTED...')
    print(url)
    try:
        server_response = requests.get(url)
        response = json.loads(server_response.text)
        if 'syncedLyrics' in response:
            status = 1
            print('Lyrics found in response.')
            error_box.configure(text = "")
            return response['syncedLyrics']  # Return lyrics data
        else:
            status = 0
            error_message = "Error: Lyrics not found in the server response."
            print(error_message)
            error_box.configure(text = "Error: Server doesn't have lyrics for this track.")
            return None  # Return None for lyrics data
    except requests.RequestException as e:        
        error_message = str(e).split("for url:")[0]  # Extract only the error message
        status = 0  # Bad, do not continue.
        print('Error:', error_message)
        return None  # Return None for lyrics data
    except KeyError as e:
        error_message = "Error parsing server response."
        print(error_message)
        return None  # Return None for lyrics data

def parse_lyrics(response): #storing timestamp and lyric text as a dictionary
    global status
    global lyrics_list

    lyrics_list = [] #used in translate() to translate lines at a time
    
    print("PARSING...")

    if status == 1:
        lyrics_dict = {}        
        lines = response.strip().split('\n')
        for line in lines:
            if match := re.match(r'\[(\d+:\d+\.\d+)\]\s*(.*)', line):
                timestamp = match[1]
                lyric = match[2]
                lyrics_list.append(lyric)
                lyrics_dict[timestamp] = lyric.strip()
        print('Parsed.')
        return lyrics_dict
    else:
        pass

def translate_batch(lines):
    print('in batch')
    try:
        translations = GoogleTranslator(source='auto', target='en').translate_batch(lines)
        print('batch translation complete.')
        return translations
    except Exception as e:
        print(f"Translation error: {e}")
        return []

def translate():
    print('in translate')
    if status == 1:
        translated = []        
        print('batching...')
        batch_size = 100  # Adjust batch size based on API limits and performance
        original_text = ""
        translated_text = ""
        for i in range(0, len(lyrics_list), batch_size):
            batch = lyrics_list[i:i+batch_size]
            translated_batch = translate_batch(batch)
            translated.extend(translated_batch)
            for original, translated_line in zip(batch, translated_batch):
                original_text += original + "\n"
                translated_text += translated_line + "\n"
                root.update()
        textbox.insert("insert", original_text)
        textbox_2.insert("insert", translated_text)
        root.update()
        return translated

def update():
    global status
    global lyrics_text
    global current_playing_new
    
    print('------------------------------')
    print('UPDATING...')
    current_playing_new = spotify_request()

    if current_playing_new == current_playing_old: #Same track. skip calls
        print('Same track. Skipping lyric and translate calls')

    else: #If current playing new != old.
        a, b, c, d= current_playing_new #format: track_name, artist_name, album_name, track_duration
        update_current_playing_old()
        print(f'Now Playing: {b} - {a}, on {c}')
        response = fetch(a,b,c,d)
        current_playing_box.configure(text = f'Now Playing: {b} - {a}, on {c}')
        if status == 1:
            lyrics_dict = parse_lyrics(response) # Store timestamp and lyric text into dict
            print("UPDATED LYRICS")
            lyrics_text = []
            lyrics_text = "\n".join(lyrics_dict.values())  # Join lyrics lines into a single string with newline
            translate()

def update_current_playing_old(): #set Old track to New one so that another the next song is compared to current and not previous
    global current_playing_new
    global current_playing_old
    
    current_playing_old = current_playing_new
    print(f'Saved new song state: {current_playing_old}')

def execute_after_mainloop():
    translate()

#calls
current_playing_old = spotify_request() #First call request
a,b,c,d = current_playing_old
response = fetch(a,b,c,d)
current_playing_box.configure(text = f'Now Playing: {b} - {a}, on {c}')
parse_lyrics(response)
button.configure(command = update)

root.mainloop()
root.after(0, execute_after_mainloop) # Execute the code regardless of root.mainloop(). If translate() is placed after root.mainloop() it wont execute.


#TODO
#inlcude jisho style addon
#include a little loading gif?
#custom icon
#look into multithreading? async load type stuff
#maybe other languages?

#ACHIEVED:
#Spotify, LRC LIB, Google Translate API calls and response + errors handling with information displayed about errors to user.
#GUI showing translated, original, and update button. Scrollable textboxes.
#Virtualised environment variables for credentials.
#Update button function: Update and show current playing song, artist, album. Also used to save API calls by comparing previously playing song and current request updated song: if same APIs not called.
#Terminal updates on what's happening, making it easier to debug.
