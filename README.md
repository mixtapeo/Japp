1. Input client_id and client_secret from your spotify developer dashboard. Make sure to check off on the 'Web API' option.
2. Click on the explorer's top bar, run these commands, one by one. This will initialise your credentials into the code:
    python -m venv env
    set env/bin/activate
    python -m pip install spotipy --upgrade pip
    set SPOTIPY_CLIENT_ID=<REPLACE THIS WITH YOUR CLIENT ID>    NOTE: USE 'export' instead of set if you use mac or linux.
    set SPOTIPY_CLIENT_SECRET=<REPLACE THIS WITH YOUR CLIENT SECRET>    
    set SPOTIPY_REDIRECT_URI=http://localhost:8888/callback
If this doesn't work, kindly open main.py and replace 'os.getenv("client_secret")' and client id with your credentials.
3. Run main.py by opening command at the containing folder (again, click on the top bar and type cmd), then:
    python main.py
4. Click on 'Approve' when asked for authorization.
