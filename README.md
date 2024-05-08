<b> NOTE:</b> Currently still under development. Achieved LRCLIB & Spotify API sync.

1. Input client_id and client_secret from your spotify developer dashboard. Make sure to check off on the 'Web API' option.

2. Click on the explorer's top bar, type 'cmd', run these commands, one by one. This will initialise your credentials into the code:
    >python -m venv env <br />
    >set env/bin/activate <br />
    >python -m pip install spotipy --upgrade pip <br />
    >set SPOTIPY_CLIENT_ID=<b>'YOUR_CLIENT_ID'</b> <br />
    >set SPOTIPY_CLIENT_SECRET=<b>'YOUR_CLIENT_SECRET'</b>  <br />
    >set SPOTIPY_REDIRECT_URI=http://localhost:8888/callback<br /><br />
<b>NOTE:</b> USE 'export' instead of set if you use mac or linux.<br />
If this doesn't work, kindly open main.py, then open the 'spotipy' library, and set the credentials in there. Might need some editing of main.py to make it work too: look at spotify_request().

3. Run main.py by opening command at the containing folder (click on the top bar and type 'cmd'), then:
    python main.py

4. Click on 'Approve' when asked for authorization.


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
