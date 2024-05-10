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
import tkinter as tk
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import time

load_dotenv() #loads .env file: gets virtuaDlised credentials from .env file. replace with credentials if needed.

client_id = os.getenv("client_id")
client_secret = os.getenv("client_secret")
redirect_uri = 'http://localhost:8888/callback'

#Functions:
def ui():                                                                           #Initialise UI elements.
    print('UI INIT')
    global t1_start
    t1_start = datetime.now()
    global root
    global error_box
    global textbox
    global textbox_2
    global button
    global current_playing_box
    global info_label
    global width
    global height
    global frame

    customtkinter.set_default_color_theme("user_themes\Hades.json")

    root = customtkinter.CTk()
    root = customtkinter.CTk()
    width: int = 1400
    height: int = 800
    root.geometry(f'{width}x{height}')
    root.title("LyriSync!")

    frame = customtkinter.CTkFrame(master=root)
    frame.pack(pady = 0, padx = 0, fill = "both", expand = True)

    textbox = customtkinter.CTkTextbox(master=frame, height=600, width = 500, corner_radius=10, font=("Noto Sans", 23))
    textbox.place(relx=0, rely=0, relwidth=0, relheight=100)
    textbox.pack(pady = 0, padx = 11, side=tk.LEFT)

    textbox_2 = customtkinter.CTkTextbox(master=frame, height=600, width = 500, corner_radius=10, font=("Noto Sans", 23))
    textbox_2.place(relx=500, rely=0, relwidth=0, relheight=1)
    textbox_2.pack(pady = 0, padx = 11, side = tk.RIGHT)

    error_box = customtkinter.CTkLabel(master=frame, width=10, corner_radius=1, text = '', font=("Noto Sans", 12))
    error_box.pack(pady = 0, padx = 10)
    
    button = customtkinter.CTkButton(master = frame, text = "Click to update...", font=("Noto Sans", 16))
    button.place(relx=800, rely=500, relwidth=100, relheight=100)
    button.pack(pady = 10, padx = 15)
    button.configure(command = update)

    current_playing_box = customtkinter.CTkLabel(master=root, width=1, height = 2, corner_radius=10, font=("Roboto", 20))
    current_playing_box.pack()

    info_label = customtkinter.CTkLabel(master=root, width=2, corner_radius=0, text = "by @mixtapeo, 2024.", font=("Noto Sans", 10))
    info_label.pack()        

    button.bind('<Escape>', lambda event: quit)

    root.mainloop()

def spotify_request():                                                              #Post request to Spotify server: playback info.
    t2_start =  datetime.now()
    print(t2_start)
    
    #spotipy credentials handlers 
    client_credentials_manager = SpotifyClientCredentials()
    sp = spotipy.Spotify(auth_manager=spotipy.SpotifyOAuth(scope='user-read-playback-state'))

    #send request for user info. scope is important.
    spotipy.prompt_for_user_token(username='', scope='user-read-playback-state', client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)

    
    try:
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
        image_url = current_playing['item']['album']['images'][0]['url']

        #debug
        print(f'track_duration (s): {track_duration}')
        print(f'track_name: {track_name}')
        print(f'artist_name: {artist_name}')
        print(f'album_name: {album_name}')
        print(f'image URL: {image_url}')
    except: #cant retrieve info of offline tracks.
        error_box.configure(text = 'Exception Occured. Maybe the song you are playing is offline / downloaded, or went over API limit.')
    t2_end =  datetime.now()
    print('Duration 2: {}'.format(t2_end - t2_start))
    
    return track_name, artist_name, album_name, track_duration, image_url

def fetch(track_name, artist_name , album_name, track_duration, image_url):         #Lyrics from LRCLIB. Uses metadata gained from spotify_request().
    print('FETCH STARTED...')
    global status
    global width
    global height
    global frame
    status = -1

    url = f'https://lrclib.net/api/get?artist_name={artist_name}&track_name={track_name}&album_name={album_name}&duration={track_duration}'
    
    try:
        server_response = requests.get(url)
        response = json.loads(server_response.text)
        if 'syncedLyrics' in response:
            status = 1
            print('Lyrics found in response.')
            error_box.configure(text = "")
            return response['syncedLyrics']             # Return lyrics data
        else:
            status = 0
            error_message = "Error: Lyrics not found in the server response."
            print(error_message)
            error_box.configure(text = "Error: Server doesn't have lyrics for this track.")
            return None                                 # Return None for lyrics data
    except requests.RequestException as e:        
        error_message = str(e).split("for url:")[0]     # Extract only the error message
        status = 0                                      # Bad, do not continue.
        print('Error:', error_message)
        return None                                     # Return None for lyrics data
    except KeyError as e:
        error_message = "Error parsing server response."
        print(error_message)
        return None                                     # Return None for lyrics data

def parse_lyrics(response):                                                         #Storing lyrics and timestamp data into lyrics_dict.
    global status
    global lyrics_list
    global start_time

    lyrics_list = []                                    #used in translate() to translate a number lines at a time
        
    print("IN PARSE")

    try:
        if status == 1:
            print("PARSING...")          
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
    except:
        pass

def translate():                                                                    #Multithreaded (4) translation by deep-translator -> Google Translate.
    global status
    global lyrics_list
    global textbox
    global textbox_2
    global start_time

    print('in translate')

    if status == 1:
                     
        original_text = ""
        translated_text = ""

        num_lines = len(lyrics_list)                                                #Divide the lyrics list into three equal parts
        chunk_size = num_lines // 3
        chunks = [lyrics_list[i:i+chunk_size] for i in range(0, num_lines, chunk_size)]
        
        def translate_chunk(chunk):                                                 #Define a function for translation
            translated_chunk = []
            for line in chunk:
                try:
                    translation = GoogleTranslator(source='auto', target='en').translate(line)
                    translated_chunk.append(translation)
                except Exception as e:
                    print(f"Translation error: {e}")
                    translated_chunk.append("")
                    error_box.config(text = "Error translating. Slow down.")
            return translated_chunk
        
        with ThreadPoolExecutor(max_workers=4) as executor:                         #Use a ThreadPoolExecutor for parallel translation
            translated_chunks = list(executor.map(translate_chunk, chunks))
            
        translated_batch = [line for chunk in translated_chunks for line in chunk]  #Concatenate translated chunks into a single list
        for original, translated_line in zip(lyrics_list, translated_batch):
            original_text += original + "\n"
            translated_text += translated_line + "\n"
            root.update()
        print('Done!')
        textbox.delete("0.0", "end") 
        textbox_2.delete("0.0", "end")         
        textbox.insert("insert", original_text) #Lyrics presented
        textbox_2.insert("insert", translated_text)
        end_time = datetime.now()
        print('Runtime (#1): {}'.format(end_time - start_time))
        root.update()

def update():                                                                       #Refresh of everything on users request.
    global status
    global lyrics_text
    global current_playing_new
    global start_time

    start_time = datetime.now()
    print('------------------------------')
    print('UPDATING...')
    current_playing_new = spotify_request()

    if current_playing_new == current_playing_old: #Same track. skip calls
        print('Same track. Skipping lyric and translate calls')

    else: #If current playing new != old.
        a, b, c, d, e= current_playing_new #format: track_name, artist_name, album_name, track_duration
        update_current_playing_old()
        print(f'Now Playing: {b} - {a}, on {c}')
        response = fetch(a,b,c,d,e)
        current_playing_box.configure(text = f'Now Playing: {b} - {a}, on {c}')
        if status == 1:
            lyrics_dict = parse_lyrics(response) # Store timestamp and lyric text into dict
            print("UPDATED LYRICS")
            lyrics_text = []
            lyrics_text = "\n".join(lyrics_dict.values())  # Join lyrics lines into a single string with newline
            translate()
            end_time = datetime.now()
            print('Runtime: {}'.format(end_time - start_time))

def update_current_playing_old():                                                   #TLDR: Was song already translated? if yes, do nothing, if no, update.
    global current_playing_new
    global current_playing_old
    
    current_playing_old = current_playing_new
    print('SAVED new song state')

def highlighter(text):                  #TODO WIP: Highlights current lyric playing.
   text.tag_add("start", "1.11","1.17")
   text.tag_config("start", background= "black", foreground= "white")

def sync_time():                        #TODO Syncs the text and time.
    pass

def execute_after_mainloop():                                               #TODO: Works, and is ancient code written for another reason. Might need to check if all of it is still needed.
    global current_playing_old
    global start_time
    print('in "jumpover" execute') 
    start_time = datetime.now()
    current_playing_old = spotify_request() #First call request
    a,b,c,d,e = current_playing_old
    response = fetch(a,b,c,d,e)
    parse_lyrics(response)
    current_playing_box.configure(text = f'Now Playing: {b} - {a}, on {c}')
    translate()

def quit():
    root.destroy()

if __name__ == "__main__":
    #Multithreading + Calls
    t1 = threading.Thread(target = ui) #Help keep the program responsive
    t2 = threading.Thread(target = execute_after_mainloop,daemon=True)
    t3 = threading.Thread(target = update, daemon=True)

    t1.start()
    t2.start()

    while True: #Keeps MainThread active forever, so that translate threads can work.
        time.sleep(1)

#TODO
#color text and background dynamically to the song image.
#inlcude non-contextual / Jisho pop up definitions. [Jisho API available: https://jisho.org/api/v1/search/words?keyword=house or JishoAPI library: https://pypi.org/project/jisho-api/]
#include a little loading gif?
#maybe other languages? +Toggleable settings w/ icon.
#synced time -> highlights current lyrical text. [+try syncing skips and rewinds]
#custom icon
#Implement user selectable API options. [+in settings cog.]

#ACHIEVED:
#MUCH improved multi-threaded translation. Without: 12-30 seconds, with: 2-10 seconds!
#Spotify, LRC LIB, Google Translate API calls and response + errors handling with information displayed about errors to user.
#GUI showing translated, original, and update button. Scrollable textboxes.
#Virtualised environment variables for credentials.
#Update button function: Update and show current playing song, artist, album. Also used to save API calls by comparing previously playing song and current request updated song: if same APIs not called.
#Terminal updates on what's happening, making it easier to debug.
#Fully commented, organised code.

#Bugs / Problems:
#If starting program and no songs playing, update pressed, program freezes.
#Thread-7 execute_after_loop keeps UI responsive, but not Thread-6 (ui) to the same extent?
#Translation times are very erratic, the same song may take between 2-5 seconds. Why? Google translate? 
