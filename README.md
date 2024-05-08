<b> NOTE:</b> Currently still under development. Achieved LRCLIB & Spotify API sync. Expect bugs.

1. Input client_id and client_secret from your spotify developer dashboard. Make sure to check off on the 'Web API' option.

2. Click on the explorer's top bar, type 'cmd', run these commands, one by one. This will initialise your credentials into the code:
    >python -m venv env <br />
    >set env/bin/activate <br />
    >python -m pip install spotipy --upgrade pip <br />
    >$env:SPOTIPY_CLIENT_ID=<b>"YOUR_CLIENT_ID"</b> <br />
    >$env:SPOTIPY_CLIENT_SECRET=<b>"YOUR_CLIENT_SECRET"</b>  <br />
    >$env:SPOTIPY_REDIRECT_URI="http://localhost:8888/callback"<br /><br />
<b>NOTE:</b> USE 'export' instead of set if you use mac or linux.<br />
<b>NOTE:</b> Above instructions are for windows 10 powershell.<br />
If this doesn't work, kindly open main.py, then open the 'spotipy' library, and set the credentials in there.
    
3. Make sure to 'pip install <requirements>' from requirements.txt.

4. Run main.py by opening command at the containing folder (click on the top bar and type 'cmd'), then:
    python main.py

5. Click on 'Approve' when asked for authorization.


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



CREDITS
spotipy: https://github.com/spotipy-dev/spotipy
deep-translator: https://github.com/nidhaloff/deep-translator?tab=readme-ov-file
