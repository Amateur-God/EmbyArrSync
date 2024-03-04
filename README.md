# EmbyArrSync

EmbyArrSync is a python script to automate the process of unmonitoring watched episodes and movies in Sonarr and Radarr and removing them from your library and file system, at default the script will only run on episodes that are older than 2 weeks/14 days, however you can configure this in the scripts settings area

You can also blacklist movies and TV shows for the script to ignore

## Setup

### Step 1 - Install Python

Make sure you have Python 3.10 or higher installed:

```
sudo apt install python3
```

### Step 2 - Download Project Files

Get the latest version using your favorite git client or by downloading the latest release from here:

https://github.com/Amateur-God/EmbyArrSync/releases

I reccomend extracting the files into its own directory in opt like "/opt/EmbyArrSync"

### Step 3 - Set up and run

#### Install requirements

navigate to the directory where you have the script

if in reccomended directory

```
cd /opt/EmbyArrSync
```

```
pip install -r requirements.txt
```

#### Get a TVDB API Key

https://thetvdb.com/dashboard/account/apikey

#### Get a TMDB API key

https://www.themoviedb.org/settings/api

#### Get a Emby User ID

Login to Emby, go to Dashboard and then to users, select the user you want the script to run for and then in the url get the userId=XXXXXXXXXXXXXXXXXX and place the X's in the EMBY_USER_ID

#### Edit Env Variables

Open EmbyArrSync.env in the config Folder with your prefered text editor and Replace the placeholders with the correct variables

if installed in its own folder in /opt

```
sudo nano /opt/EmbyArrSync/config/EmbyArrSync.env
```

```py
# TV and Movie Handling Logic
HANDLE_TV = True # Set to false to disable the script from touching TV shows
HANDLE_MOVIES = True # Set to false to disable the script from touching Movies shows
TV_DELETE = True # Set to false to disable the script from Deleting TV shows
MOVIE_DELETE = True # Set to false to disable the script from Deleting Movies shows


# Sonarr API details
SONARR_API_KEY = 'SONARR_API_KEY'
SONARR_URL = 'http://IP:PORT/api/v3'

# Radarr API details
RADARR_API_KEY = 'RADARR_API_KEY'
RADARR_URL = 'http://IP:PORT/api/v3'

# Emby API details
EMBY_API_KEY = 'EMBY_API_KEY'
EMBY_URL = 'http://IP:PORT/emby'
EMBY_USER_ID = 'EMBY_USER_ID' # This is the UID for a user not username get this from the user= section of the URL when you click on a user in the users tab of the dashboard
#  Currently set to the highest number this is the maximum number of watched items to fetch from emby, change this if you only want to get the last X watched items
LIMIT = 1000000000 
# boolean value (True/False) Set to true if you want the script to handle deleting from emby library, 
# set to false if you are using the Sonarr/Radarr connect functions to handle emby library updates
EMBY_DELETE = False 

#tvdb/tmdb
TVDB_API_KEY = 'TVDB_API_KEY'
TVDB_PIN = 'THIS CAN BE ANY STRING OF NUMBERS YOU WANT'
TMDB_API_KEY = 'TMDB_API_KEY'

# If Aired in this time period dont delete
# Set the number of days to the time period from show air date that you want to be blacklisted from deleting

DAYS = 14
```

#### Blacklist Tv shows and Movies

Open blacklists.json in the config Folder with your prefered text editor and Replace the placeholders with the correct variables, or delete the examples to make an empty list if you dont want to blacklist any shows

if installed in its own folder in /opt

```
sudo nano /opt/EmbyArrSync/config/blacklists.json
```

```json
{
    "BLACKLISTED_MOVIES": [
      "Example Movie 1",
      "Example Movie 2",
      "Example Movie 3"
    ],
    "BLACKLISTED_TV_SHOWS": [
      "Example TV Show 1",
      "Example TV Show 2",
      "Example TV Show 3",
      "Example TV Show 4"
    ],
    "BLACKLISTED_PATHS": [
      "/a/path/to/blacklist",
      "/another/path/to/blacklist"
    ]
  }
  
```

#### Run on linux

This assumes you moved the script file to its own folder in opt

```bash
sudo chmod a+x /opt/EmbyArrSync/EmbyArrSync.py
```

```bash
cd /opt/EmbyArrSync
```

```bash
python3 ./EmbyArrSync
```

### Step 4 - Optional Setup (Auto run via systemd)

This isnt the only way to set it up to autorun its just my prefered method you can also set a cron job up to run it on a set schedule

Enter the following command into your terminal to create a new service file. 
replacing nano with your preferred text editor

```bash
sudo nano /etc/systemd/system/EmbyArrSync.service
```

Paste the contents of the following into the new file
replacing the `/opt/EmbyArrSync/` and `#USER#` with the correct ones for your install

```bash
[Unit]
Description=EmbyArrSync
After=multi-user.target
[Service]
Type=simple
User=#USER#
ExecStart=/bin/bash -c 'cd /opt/EmbyArrSync/ && python3 EmbyArrSync.py'
[Install]
WantedBy=multi-user.target
```

```bash
sudo nano /etc/systemd/system/EmbyArrSync.timer
```

```bash
[Unit]
Description= Run EmbyArrSync Periodically

[Timer]
OnBootSec=1min
OnUnitActiveSec=120min #Change to how often you want the script to run

[Install]
WantedBy=timers.target
```

Then run the following commands to start the service and enable it at boot

#### Reload the daemon for the latest files
```bash
sudo systemctl daemon-reload
```

#### Start the Service
```bash
sudo systemctl start EmbyArrSync.timer
```

#### Check the service is running
```bash
sudo systemctl status EmbyArrSync.timer
```

#### Enable at boot
```bash
sudo systemctl enable EmbyArrSync.timer
```
