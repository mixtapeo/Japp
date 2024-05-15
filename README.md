<h2> Features </h2>
<b> NOTE:</b> Development is paused. Expect bugs.

![image](https://github.com/mixtapeo/LyriSync/assets/64733018/a9f4c73f-d461-4710-93b2-06ba6788c656)
<h4>Sync your spotify songs with LyriSync for automatic lyrics & translations!</h4>
Currently working on in-place definitions. This app is aimed at language learners.

<h2> Installation </h2>
Video tutorial: https://youtu.be/BnLlqjDA4aM <br /><br />
Note: Updated video will be posted at some point <br /><br />

Instructions:
1. Input client_id and client_secret from your spotify developer dashboard. Make sure to check off on the 'Web API' option.

2. Click on the explorer's top bar, type 'cmd', run these commands, one by one. This will initialise your credentials into the code:
    >python -m venv env <br />
    >set env/bin/activate <br />
    >python -m pip install spotipy --upgrade pip <br />
    >$env:SPOTIPY_CLIENT_ID=<b>"YOUR_CLIENT_ID"</b> <br />
    >$env:SPOTIPY_CLIENT_SECRET=<b>"YOUR_CLIENT_SECRET"</b>  <br />
    >$env:SPOTIPY_REDIRECT_URI="http://localhost:8888/callback"<br /><br />
<b>NOTE:</b> Use 'export' instead of set if you use mac or linux.<br />
<b>NOTE:</b> Above instructions are for windows 10 powershell / terminal, in VSCode.<br />
If this doesn't work, kindly open main.py, then open the 'spotipy' library, and set the credentials in there.
    
3. Make sure to 'pip install <requirements>' from requirements.txt, or manually pip installing each requirement.

4. Run main.py by opening command at the containing folder (click on the top bar and type 'cmd'), then:
    python main.py

5. Click on 'Approve' when asked for authorization.

<h2>To-do / done</h2>
<h4>Todo List</h4>

#color text and background dynamically to the song image.<br />
#inlcude non-contextual / Jisho pop up definitions. <h6>[Jisho API available: https://jisho.org/api/v1/search/words?keyword=house or JishoAPI library: https://pypi.org/project/jisho-api/]</h6> <br />
#include a little loading gif?<br />
#maybe other languages? +Toggleable settings w/ icon.<br />
#synced time -> highlights current lyrical text. [+try syncing skips and rewinds]<br />
#custom icon
#Implement user selectable API options. [+in settings cog.]<br />

<h4>ACHIEVED:</h4>
#MUCH improved multi-threaded translation. Without: 12-30 seconds, with: 2-10 seconds!<br />
#Spotify, LRC LIB, Google Translate API calls and response + errors handling with information displayed about errors to user.<br />
#GUI showing translated, original, and update button. Scrollable textboxes.<br />
#Virtualised environment variables for credentials.<br />
#Update button function: Update and show current playing song, artist, album. Also used to save API calls by comparing previously playing song and current request updated song: if same APIs not called.<br />
#Terminal updates on what's happening, making it easier to debug.<br />
#Fully commented, organised code.<br />

<h4>#Bugs / Problems:</h4>
#If starting program and no songs playing, update pressed, program freezes.<br />
#Thread-7 execute_after_loop keeps UI responsive, but not Thread-6 (ui) to the same extent?<br />
#Translation times are very erratic, the same song may take between 2-5 seconds. Why? Google translate? <br />



<h2>CREDITS</h2>
spotipy: https://github.com/spotipy-dev/spotipy<br />
deep-translator: https://github.com/nidhaloff/deep-translator?tab=readme-ov-file<br />
customtkinter: https://github.com/TomSchimansky/CustomTkinter
