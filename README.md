1. Input client_id and client_secret from your spotify developer dashboard. Make sure to check off on the 'Web API' option.

2. Click on the explorer's top bar, type 'cmd', run these commands, one by one. This will initialise your credentials into the code:
    >python -m venv env <br />
    >set env/bin/activate <br />
    >python -m pip install spotipy --upgrade pip <br />
    >set SPOTIPY_CLIENT_ID=<b>'YOUR_CLIENT_ID'</b>
    >set SPOTIPY_CLIENT_SECRET=<b>'YOUR_CLIENT_SECRET'</b>  <br />
    >set SPOTIPY_REDIRECT_URI=http://localhost:8888/callback<br /><br />
<b>NOTE:</b> USE 'export' instead of set if you use mac or linux.<br />
If this doesn't work, kindly open main.py and replace 'os.getenv("client_secret")' and client id with your credentials.

3. Run main.py by opening command at the containing folder (click on the top bar and type 'cmd'), then:
    python main.py

4. Click on 'Approve' when asked for authorization.
