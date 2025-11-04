# EmbyArrSync

EmbyArrSync is a Python script designed to automate the management of watched episodes and movies in Sonarr and Radarr. By default, it unmonitors content that's older than two weeks (14 days) and removes them from both your library and file system. However, this timeframe is adjustable through environment variables.

The script includes options to exclude specific movies, TV shows, and directories through a blacklist feature. Users can configure various options via environment variables, including whether to delete content in Emby, Sonarr, or Radarr, and whether to skip deletion for content marked as a favorite in Emby. Additionally, there are environment variables available to disable handling either movies or TV shows entirely, providing further customization to meet specific needs.

> [!NOTE]
> **Enjoying this integration?**
>
> This is an open-source project I maintain in my spare time. If you'd like to show your appreciation and support its development, you can buy me a coffee!
>
> [![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/amateurgod)


## Setup

### Step 1 - Install Python

Make sure you have Python 3.10 or higher installed:

```
sudo apt install python3 python3-venv
```

### Step 2 - Download Project Files

Get the latest version using your favorite git client or by downloading the latest release from here:

https://github.com/Amateur-God/EmbyArrSync/releases

I reccomend extracting the files into its own directory in opt like "/opt/EmbyArrSync"

### Step 3 - Set up and run

#### Install requirements

```bash
# Go to your folder (adjust for your actual path)
cd /opt/EmbyArrSync

# Create a virtual environment named 'venv'
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Upgrade pip (recommended)
pip install --upgrade pip

# Install project requirements
pip install requirements.txt
```


#### Get a TMDB API key

https://www.themoviedb.org/settings/api

#### Get a Emby User ID

Login to Emby, go to Dashboard and then to users, select the user you want the script to run for and then in the url get the userId=XXXXXXXXXXXXXXXXXX and place the X's in the EMBY_USER_ID

#### Edit Env Variables

Open EmbyArrSync.env in the config Folder with your prefered text editor and Replace the placeholders with the correct variables

Warning setting "IGNORE_FAVOURITES" to False means the script will run on items that are favourited in emby, Setting to true means items Favourited in emby will be blacklisted and ignored by the script

It is reccomended to lower the limit after first run, this limit is just as high as possible so that first run gets as many watched shows as possible.

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
IGNORE_FAVOURITES = True # Set to True if you want the script to ignore items that are marked as favourites in emby (Not Unmonitor and Not Delete)


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

#tmdb
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
python3 EmbyArrSync.py
```

### Step 4 - Optional Setup (Auto run via systemd)

This isnt the only way to set it up to autorun its just my prefered method you can also set a cron job up to run it on a set schedule

Enter the following command into your terminal to create a new service file. 
replacing nano with your preferred text editor

```bash
sudo nano /etc/systemd/system/EmbyArrSync.service
```

Paste the following, replacing `/opt/EmbyArrSync/` and `#USER#` as needed.  
**NOTE:** If using venv, you must activate it in the `ExecStart` line:

```ini
[Unit]
Description=EmbyArrSync
After=multi-user.target

[Service]
Type=simple
User=#USER#
WorkingDirectory=/opt/EmbyArrSync
ExecStart=/bin/bash -c 'source /opt/EmbyArrSync/venv/bin/activate && python3 EmbyArrSync.py'

[Install]
WantedBy=multi-user.target
```

```bash
sudo nano /etc/systemd/system/EmbyArrSync.timer
```

```ini
[Unit]
Description= Run EmbyArrSync Periodically

[Timer]
OnBootSec=1min
OnUnitActiveSec=120min   # Change as needed for run frequency

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

---

## Troubleshooting

- If you get a `ModuleNotFoundError` for any package, ensure your virtual environment is activated (`source venv/bin/activate`).
- If permissions are denied, check file and folder ownership.
- With systemd, always specify the full path for your venv activation if running as a different user.

---

## Contributing

PRs and issues are welcome!  
If you make improvements, please submit them for review.

---

**Enjoy!**  
If you like this tool, consider supporting further development:  
[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/amateurgod)
