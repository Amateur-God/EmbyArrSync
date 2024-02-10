# EmbyArrSync

EmbyArrSync is a python script to automate the process of unmonitoring watched episodes and movies in Sonarr and Radarr and removing them from your library and file system, as of now the script will only run on episodes that are older than 2 weeks/14 days

## Setup

### Step 1 - Install Python

Make sure you have Python 3.10 or higher installed:

### Step 2 - Download Project Files

Get the latest version using your favorite git client or by downloading the latest release from here:

### Step 3 - Set up and run

#### Get a TVDB API Key

https://thetvdb.com/dashboard/account/apikey

#### Get a TMDB API key

https://www.themoviedb.org/settings/api

#### Edit Env Variables

Open the EmbyArrSync.py with your prefered text editor and and edit the following env variables that can be found at the top of the file

```py
# Sonarr API details
SONARR_API_KEY = 'SONARR_API_KEY'
SONARR_URL = 'http://IP:PORT/api/v3'

# Radarr API details
RADARR_API_KEY = 'RADARR_API_KEY'
RADARR_URL = 'http://IP:PORT/api/v3'

# Emby API details
EMBY_API_KEY = 'EMBY_API_KEY'
EMBY_URL = 'http://IP:PORT/emby'
EMBY_USER_ID = 'EMBY_USER_ID'

#tvdb/tmdb
TVDB_API_KEY = 'TVDB_API_KEY'
TVDB_PIN = 'THIS CAN BE ANY STRING OF NUMBERS YOU WANT'
TMDB_API_KEY = 'TMDB_API_KEY'

# Blacklisted movies and TV shows
BLACKLISTED_MOVIES = ["Example Movie 1", "Example Movie 2"]
BLACKLISTED_TV_SHOWS = ["Example Show 1", "Example Show 2"]
```

#### linux

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

### Step 4 - Otional Setup (Auto run via systemd)

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
