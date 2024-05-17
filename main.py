import spotipy
import os
import requests
import json
import re
from dotenv import load_dotenv
from deep_translator import GoogleTranslator
from pprint import pprint
import customtkinter
import tkinter as tk
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import time
from PIL import Image
import urllib.request

#Functions:
class LyriSyncApp(customtkinter.CTk):    
    width = 1400
    height = 700

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        global t1_start
        print('UI INIT')
        
        t1_start = datetime.now()

        customtkinter.set_default_color_theme("user_themes\Hades.json")        
        self.geometry(f"{self.width}x{self.height}")
        self.title("LyriSync!")
        
        # Frames for each object category. Only center has more than 1 object.
        self.frame_left = customtkinter.CTkFrame(master=self)
        self.frame_right = customtkinter.CTkFrame(master=self)
        self.frame_center = customtkinter.CTkFrame(master=self)
        self.frame_top = customtkinter.CTkFrame(master=self)
        self.frame_center_2 = customtkinter.CTkFrame(master=self)


        self.frame_left.pack(side = "left", fill = "both", expand = True)
        self.frame_right.pack(side = "right", fill = "both", expand = True)
        self.frame_center.pack(side = "bottom", fill = "both", expand = True)
        self.frame_center_2.pack(side = "bottom", fill = "x", expand = False)
        self.frame_top.pack(side = "bottom", fill = "both", expand = True)

        self.create_widgets()

    def create_widgets(self):        
        font = "Noto Sans"

        # Textbox 1 : Original Text
        self.textbox = customtkinter.CTkTextbox(master=self.frame_left, height=10, width=50, corner_radius=5, font=(font, 20))
        self.textbox.place(relx=0, rely=0, relwidth=0, relheight=10)
        self.textbox.pack(pady = 0, padx = 11, expand = True, fill = 'both')

        # Textbox 2 : Translations
        self.textbox_2 = customtkinter.CTkTextbox(master=self.frame_right, height=10, width=50, corner_radius=5, font=(font, 20))
        self.textbox_2.tag_config('tag',justify = tk.CENTER)
        self.textbox_2.place(relx=500, rely=0, relwidth=0, relheight=1)
        self.textbox_2.pack(pady = 0, padx = 10, expand = True, fill = 'both')
        
        # Dictionary box: is a label better?
        self.refer_box = customtkinter.CTkTextbox(master=self.frame_center, height=10, width=50, corner_radius=5, font=(font, 16))
        self.refer_box.place(relx=500, rely=0, relwidth=0, relheight=1)
        self.refer_box.pack(pady = 2, padx = 2, expand = True, fill = 'both')

        # Error box
        self.error_box = customtkinter.CTkLabel(master=self.frame_center, width=10, corner_radius=1, text = '', font=(font, 12))
        self.error_box.pack(pady = 0, padx = 10)

        # Current playing label
        self.current_playing_label = customtkinter.CTkLabel(master=self.frame_top, font=(font, 14), wraplength=230)
        self.current_playing_label.pack()

        # Click to update button
        self.button = customtkinter.CTkButton(master=self.frame_center, text="Click to update...", font=(font, 16))
        self.button.place(relx=800, rely=500, relwidth=100, relheight=100)
        self.button.pack(pady = 10, padx = 15)
        self.button.configure(command = self.update)

        # Info label
        self.info_label = customtkinter.CTkLabel(master=self.frame_top, width=2, corner_radius=0, text = "by @mixtapeo, 2024.", font=(font, 10))
        self.info_label.configure(text = 'by @mixtapeo, 2024.', justify='center')
        self.info_label.pack()
        
        # Init cover label
        self.cover_label = customtkinter.CTkLabel(master=self.frame_center_2, text = '', width = 200, height = 200) #controls size of center frame

    def spotify_request(self):                                                              #Post request to Spotify server: playback info.
        t2_start =  datetime.now()
        print(t2_start)
        
        #spotipy credentials handlers 
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
            self.error_box.configure(text = 'Exception Occured. Maybe the song you are playing is offline / downloaded, or went over API limit.')
        t2_end =  datetime.now()
        print('Duration 2: {}'.format(t2_end - t2_start))
        
        # Display cover image
        urllib.request.urlretrieve(image_url, "cover.png")
        cover_image = customtkinter.CTkImage(Image.open("cover.png"), size = (250, 250))
        self.cover_label.configure(image = '')
        self.cover_label.configure(image = cover_image)
        self.cover_label.pack(pady = 2, padx = 2, expand = True, fill = 'both')
        
        
        return track_name, artist_name, album_name, track_duration

    def fetch(self, track_name, artist_name , album_name, track_duration):         #Lyrics from LRCLIB. Uses metadata gained from spotify_request().
        print('FETCH STARTED...')
        global status
        status = -1

        url = f'https://lrclib.net/api/get?artist_name={artist_name}&track_name={track_name}&album_name={album_name}&duration={track_duration}'
        
        try:
            server_response = requests.get(url)
            response = json.loads(server_response.text)
            if 'syncedLyrics' in response:
                status = 1
                print('Lyrics found in response.')
                self.error_box.configure(text = "",)                
                return response['syncedLyrics']             # Return lyrics data
            else:
                status = 0
                error_message = "Error: Lyrics not found in the server response."
                print(error_message)
                self.error_box.configure(text = "Error: Server doesn't have lyrics for this track.")
                self.center_new_text(self.textbox, '')
                self.center_new_text(self.textbox_2, '')
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

    def parse_lyrics(self, response):                                                         #Storing lyrics and timestamp data into lyrics_dict.
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

    def translate(self):                                                                    #Multithreaded (4) translation by deep-translator -> Google Translate.
        global status
        global lyrics_list
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
                        self.error_box.config(text = "Error translating. Slow down (probably went over googletranslate API call limit).")
                return translated_chunk 
            
            with ThreadPoolExecutor(max_workers=4) as executor:                         #Use a ThreadPoolExecutor for parallel translation
                translated_chunks = list(executor.map(translate_chunk, chunks))
                
            translated_batch = [line for chunk in translated_chunks for line in chunk]  #Concatenate translated chunks into a single list
            
            for original, translated_line in zip(lyrics_list, translated_batch):
                original_text += original + "\n"
                translated_text += translated_line + "\n"   

            print('Done!')

            self.center_new_text(self.textbox, original_text) #Lyrics printed
            self.center_new_text(self.textbox_2, translated_text)

            end_time = datetime.now()
            print('Runtime (#1): {}'.format(end_time - start_time))            
    
    def update(self):                                                                       #Refresh of everything on users request.
        global status
        global lyrics_text
        global current_playing_new
        global start_time

        start_time = datetime.now()
        print('------------------------------')
        print('UPDATING...')
        current_playing_new = self.spotify_request()

        if current_playing_new == current_playing_old: #Same track. skip calls
            print('Same track. Skipping lyric and translate calls')

        else: #If current playing new != old.
            a, b, c, d= current_playing_new #format: track_name, artist_name, album_name, track_duration
            self.update_current_playing_old()
            print(f'Now Playing: {b} - {a}')
            response = self.fetch(a,b,c,d)
            self.current_playing_label.configure(text = f'Now Playing: {b} - {a}')
            if status == 1:
                lyrics_dict = self.parse_lyrics(response) # Store timestamp and lyric text into dict
                print("UPDATED LYRICS")
                lyrics_text = []
                lyrics_text = "\n".join(lyrics_dict.values())  # Join lyrics lines into a single string with newline
                self.translate()
                end_time = datetime.now()
                print('Runtime: {}'.format(end_time - start_time))

    def update_current_playing_old(self):                                                   #TLDR: Was song already translated? if yes, do nothing, if no, update.
        global current_playing_new
        global current_playing_old
        
        current_playing_old = current_playing_new
        print('SAVED new song state')
                  
    def highlighter(self, text):                  #TODO WIP: Highlights current lyric playing. Try working with index of text in textbox, changing its color, and using syncedTime info

        text.tag_add("start", "1.11","1.17")
        text.tag_config("start", background= "black", foreground= "white")

    def execute_after_mainloop(self):                                               #TODO: Works, and is ancient code written for another reason. Might need to check if all of it is still needed.
        global current_playing_old
        global start_time

        print('in "jumpover" execute') 
        start_time = datetime.now()

        current_playing_old = app.spotify_request() #First call request
        a,b,c,d = current_playing_old
        response = self.fetch(a,b,c,d)
        self.parse_lyrics(response)
        self.current_playing_label.configure(text = f'Now Playing: {b} - {a}')
        self.translate()

    def center_new_text(self, object, text):
        object.delete("0.0", "end")
        object.tag_config("centertag", justify='center')
        object.insert("insert", text)
        object.tag_add("centertag", "1.0", "end")

    def sync_time(self):                        #TODO Syncs the text and time.
        pass

if __name__ == "__main__":
    app = LyriSyncApp()

    load_dotenv() #loads .env file: gets virtuaDlised credentials from .env file. replace with credentials if needed.

    client_id = os.getenv("client_id")
    client_secret = os.getenv("client_secret")
    redirect_uri = 'http://localhost:8888/callback'
    #Multithreading + Calls    
    t2 = threading.Thread(target = app.execute_after_mainloop,daemon=True) # Help keep the program responsive
    t3 = threading.Thread(target = app.update, daemon=True)

    t2.start()

    app.mainloop()

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
#Update button function: Update and show current playing song, artist, album and display cover. 
#Saved API calls by comparing previously playing song and current request updated song: if same APIs not called.
#Terminal updates on what's happening, making it easier to debug.
#Fully commented, organised code.

#Bugs / Problems:
#If starting program and no songs playing, update pressed, program freezes.
#Thread-7 execute_after_loop keeps UI responsive, but not Thread-6 (ui) to the same extent?
#Translation times are very erratic, the same song may take between 2-5 seconds. Why? Google translate? 