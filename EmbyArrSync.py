import requests
from flask import Flask, request

app = Flask(__name__)

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

# Blacklisted movies and TV shows
BLACKLISTED_MOVIES = []
BLACKLISTED_TV_SHOWS = []

def get_watched_items(user_id):
    url = f"{EMBY_URL}/Users/{user_id}/Items/Latest"
    params = {
        'IsFolder': 'false',
        'IsPlayed': 'true',
        'GroupItems': 'false',
        'EnableImages': 'false',
        'EnableUserData': 'false',
        'api_key': EMBY_API_KEY
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        watched_items = response.json()
        return watched_items
    else:
        print("Error fetching watched items from Emby")
        return None

def get_ext_id(item_id):
    url = f"{EMBY_URL}/Items/{item_id}/ExternalId"
    params = {'api_key': EMBY_API_KEY}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if 'Tvdb' in data:
            return data['Tvdb']
        if 'Tmdb' in data:
            return data['Tmdb']
    return None

def get_episode_info(series_id, season_number):
    url = f"{SONARR_URL}/episode"
    params = {
        'seriesId': series_id,
        'seasonNumber': season_number,
        'includeImages': 'false',
        'apikey': SONARR_API_KEY
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching episode info: {response.status_code}")
        return None

def get_series_id_by_tvdb(tvdb_id):
    url = f"{SONARR_URL}/series"
    params = {
        'tvdbId': tvdb_id,
        'includeSeasonImages': 'false',
        'apikey': SONARR_API_KEY
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        series_info = response.json()
        if series_info:
            return series_info[0]['id']  # Assuming the first series is the correct one
    else:
        print(f"Error fetching series by TVDB ID: {response.status_code}")
    return None

def unmonitor_episodes(episode_ids, monitored):
    url = f"{SONARR_URL}/episode/monitor"
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'apikey': SONARR_API_KEY  # Note: Header 'apikey' is not standard and may not work; typically API key is a query param
    }
    payload = {
        'episodeIds': episode_ids,
        'monitored': monitored
    }
    response = requests.put(url, headers=headers, json=payload)
    if response.status_code == 200:
        print("Monitoring status changed successfully.")
    else:
        print(f"Error changing monitoring status: {response.status_code}")

def delete_episode_file(file_id):
    url = f"{SONARR_URL}/episodefile/{file_id}"
    params = {
        'apikey': SONARR_API_KEY
    }
    response = requests.delete(url, params=params)
    if response.status_code == 200:
        print("Episode file deleted successfully.")
    else:
        print(f"Error deleting episode file: {response.status_code}")

def get_movie_info_by_tmdb(tmdb_id):
    url = f"{RADARR_URL}/movie"
    params = {
        'tmdbId': tmdb_id,
        'excludeLocalCovers': 'false',
        'apikey': RADARR_API_KEY
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching movie info for TMDB ID {tmdb_id}: {response.status_code}")
        return None
    
def unmonitor_movies(radarr_id, monitored):
    url = f"{RADARR_URL}/movie/{radarr_id}"
    params = {
        'moveFiles': 'false',
        'apikey': RADARR_API_KEY
    }
    payload = {
        'monitored': monitored
    }
    headers = {
        'accept': 'text/plain',
        'Content-Type': 'application/json'
    }
    response = requests.put(url, params=params, json=payload, headers=headers)
    if response.status_code == 200:
        print(f"Monitoring status updated for movie ID {radarr_id}.")
    else:
        print(f"Error updating monitoring status for movie ID {radarr_id}: {response.status_code}")

def delete_movie(radarr_id, delete_files=False, add_import_exclusion=False):
    url = f"{RADARR_URL}/movie/{radarr_id}"
    params = {
        'deleteFiles': str(delete_files).lower(),
        'addImportExclusion': str(add_import_exclusion).lower(),
        'apikey': RADARR_API_KEY
    }
    response = requests.delete(url, params=params)
    if response.status_code == 200:
        print(f"Movie ID {radarr_id} deleted successfully.")
    else:
        print(f"Error deleting movie ID {radarr_id}: {response.status_code}")