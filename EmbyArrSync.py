
##########################
## DO NOT CHANGE THE BELOW
##########################


from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import requests
import json
import re 

# Load environment variables from .env file
env_file = 'config/EmbyArrSync.env'
load_dotenv(dotenv_path=env_file)

IGNORE_FAVOURITES = os.getenv('IGNORE_FAVOURITES', 'False') == 'True'
HANDLE_TV = os.getenv('HANDLE_TV', 'False') == 'True'
HANDLE_MOVIES = os.getenv('HANDLE_MOVIES', 'False') == 'True'
TV_DELETE = os.getenv('TV_DELETE', 'False') == 'True'
MOVIE_DELETE = os.getenv('MOVIE_DELETE', 'False') == 'True'

SONARR_API_KEY = os.getenv('SONARR_API_KEY')
SONARR_URL = os.getenv('SONARR_URL')

RADARR_API_KEY = os.getenv('RADARR_API_KEY')
RADARR_URL = os.getenv('RADARR_URL')

EMBY_API_KEY = os.getenv('EMBY_API_KEY')
EMBY_URL = os.getenv('EMBY_URL')
EMBY_USER_ID = os.getenv('EMBY_USER_ID')
EMBY_DELETE = os.getenv('EMBY_DELETE', 'False') == 'True'  # Convert string to boolean
LIMIT = int(os.getenv('LIMIT', '1000000000'))

TVDB_API_KEY = os.getenv('TVDB_API_KEY')
TVDB_PIN = os.getenv('TVDB_PIN')
TMDB_API_KEY = os.getenv('TMDB_API_KEY')

DAYS = int(os.getenv('DAYS', 14))  # Default to 14 if not defined
# Load blacklists from JSON file
with open('config/blacklists.json', 'r') as file:
    blacklists = json.load(file)

BLACKLISTED_TV_SHOWS = blacklists.get('BLACKLISTED_TV_SHOWS', [])
BLACKLISTED_MOVIES = blacklists.get('BLACKLISTED_MOVIES', [])
BLACKLISTED_PATHS = blacklists.get('BLACKLISTED_PATHS', []) 


def get_series_info(user_id):
    url = f"{EMBY_URL}/Users/{user_id}/Items/Latest"
    params = {
        'IsFolder': 'false',
        'IsPlayed': 'true',
        'GroupItems': 'true',
        'EnableImages': 'false',
        'EnableUserData': 'true',
        'Fields': 'Path',
        'Limit': LIMIT,
        'api_key': EMBY_API_KEY
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        watched_items = response.json()
        return watched_items
    else:
        print(f"Error fetching series info from Emby: {response.status_code}, {response.text}")
        return None
    
def get_watched_items(user_id):
    url = f"{EMBY_URL}/Users/{user_id}/Items/Latest"
    params = {
        'IsFolder': 'false',
        'IsPlayed': 'true',
        'GroupItems': 'false',
        'EnableImages': 'false',
        'EnableUserData': 'true',
        'Fields': 'Path',
        'Limit': LIMIT,
        'api_key': EMBY_API_KEY
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        watched_items = response.json()
        return watched_items
    else:
        print(f"Error fetching watched items from Emby: {response.status_code}, {response.text}")
        return None
    
def get_tmdb_id(movie_name, movie_path):
    # Try to extract TMDBID from the path
    match = re.search(r'tmdbid-(\d+)', movie_path)
    if match:
        return match.group(1) # Returns the first matching group (the ID)
    # If the ID is not found in the path, proceed to search via the API
    search_url = f'https://api.themoviedb.org/3/search/movie'
    params = {
        'api_key': TMDB_API_KEY,
        'query': movie_name
    }
    response = requests.get(search_url, params=params)
    if response.status_code == 200:
        results = response.json().get('results', [])
        if results:
            # Assuming you want the first result
            first_result = results[0]
            return first_result.get('id')
    else:
        print(f"Error searching TMDB for {movie_name}: {response.status_code}, {response.text}")
    return None

def get_tvdb_token():
    url = 'https://api4.thetvdb.com/v4/login'
    headers = {'Content-Type': 'application/json'}
    data = {
        "apikey": TVDB_API_KEY,
        "pin": TVDB_PIN
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        token_response = response.json()
        token = token_response.get('data', {}).get('token')
        return token
    else:
        print(f"Failed to obtain TVDB token: {response.status_code}, {response.text}")
        return None

TVDB_TOKEN = get_tvdb_token()

def get_tvdb_id(series_name, series_path):
    # Try to extract TVDBID from the path
    match = re.search(r'tvdbid-(\d+)', series_path)
    if match:
        return match.group(1)  # Returns the first matching group (the ID)
    # If the ID is not found in the path, proceed to search via the API
    search_url = f"https://api4.thetvdb.com/v4/search?query={series_name}"
    headers = {
        'Authorization': f'Bearer {TVDB_TOKEN}',
        'Content-Type': 'application/json'
    }
    params = {'query': series_name, 'type': 'series'}  # Assuming you're searching for series
    response = requests.get(search_url, headers=headers, params=params)

    if response.status_code == 200:
        results = response.json().get('data', [])
        if results:
            # Assuming the first result is what you want
            return results[0].get('tvdb_id')
        else:
            print(f"No results found for {series_name}")
            return None
    else:
        print(f"Failed to search TVDB for {series_name}: {response.status_code}, {response.text}")
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
        print(f"Error fetching episode info: {response.status_code}, {response.text}")
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
        print(f"Error fetching series by TVDB ID: {response.status_code}, {response.text}")
    return None

def fetch_episode_status(episode_id):
    """Fetch the current monitoring status of a specific episode."""
    episode_info_url = f"{SONARR_URL}/episode/{episode_id}?apikey={SONARR_API_KEY}"
    response = requests.get(episode_info_url)
    if response.status_code == 200:
        episode_info = response.json()
        return episode_info.get('monitored')
    else:
        print(f"Error fetching episode info: {response.status_code}, {response.text}")
        return None  # Indicates an error occurred, consider how you wish to handle this.

def unmonitor_episodes(episode_ids):
    """Unmonitor episodes if they are currently monitored."""
    episodes_to_unmonitor = []

    # First, check if each episode is monitored
    for episode_id in episode_ids:
        if fetch_episode_status(episode_id):
            episodes_to_unmonitor.append(episode_id)

    if not episodes_to_unmonitor:
        return

    # Now, unmonitor episodes that are currently monitored
    url = f"{SONARR_URL}/episode/monitor?apikey={SONARR_API_KEY}"
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
    }
    payload = {
        'episodeIds': episodes_to_unmonitor,
        'monitored': False
    }
    response = requests.put(url, headers=headers, json=payload)
    if response.status_code in [200, 202]:
        print(f"Monitoring status changed successfully for episodes: {episodes_to_unmonitor}")
    else:
        print(f"Error changing monitoring status: {response.status_code}, {response.text}")

def get_movie_info(tmdb_id, movie_name):
    url = f"{RADARR_URL}/movie/lookup/tmdb/{tmdb_id}?apikey={RADARR_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        movie_info = response.json()
        # Ensure movie_info is a list and has at least one element
        if isinstance(movie_info, list) and len(movie_info) > 0:
            # Assuming the first movie in the list is the one you want
            return movie_info[0]  
        else:
            print(f"No movies found for radarr for {movie_name}: {response.status_code}, {response.text}")
            return None
    if response.status_code == 404:
        print(f"{movie_name} Not found in Radarr Library")
    else:
        print(f"Error fetching movie info from radarr for {movie_name}: {response.status_code}, {response.text}")
        return None
    
def fetch_movie_status(radarr_id, movie_name):
    """Fetch the current monitoring status of a specific movie."""
    movie_info_url = f"{RADARR_URL}/movie/{radarr_id}?apikey={RADARR_API_KEY}"
    response = requests.get(movie_info_url)
    if response.status_code == 200:
        movie_info = response.json()
        return movie_info.get('monitored')
    else:
        print(f"Error fetching movie status from radarr for {movie_name}: {response.status_code}, {response.text}")
        return None 

def unmonitor_movies(radarr_id, movie_name):
    """Unmonitor a movie if it is currently monitored."""
    # First, check if the movie is monitored
    if fetch_movie_status(radarr_id, movie_name):
        url = f"{RADARR_URL}/movie/{radarr_id}?apikey={RADARR_API_KEY}"
        payload = {
            'monitored': False
        }
        headers = {
            'accept': 'text/plain',
            'Content-Type': 'application/json'
        }
        response = requests.put(url, json=payload, headers=headers)
        if response.status_code in [200, 202]:
            print(f"Monitoring status updated for {movie_name}.")
        else:
            print(f"Error updating monitoring status for {movie_name}: {response.status_code}, {response.text}")
    else:
        print(f"{movie_name} is already unmonitored.")

def delete_item(item_id, item_info):
    url = f"{EMBY_URL}/Items?{item_id}&api_key={EMBY_API_KEY}"
    response = requests.delete(url)
    if response.status_code == 204:
        print(f"Item {item_info} deleted successfully from Emby.")
    else:
        print(f"Failed to delete item {item_info} from Emby: {response.status_code}, {response.text}")

def delete_episode_file(series_id, season_number, episode_number, episode_name, series_name):
    episodes = get_episode_info(series_id, season_number)
    episode_file_id = None
    for episode in episodes:
        if episode['episodeNumber'] == episode_number and episode['hasFile']:
            episode_file_id = episode['episodeFileId']
            break

    if episode_file_id:
        delete_url = f"{SONARR_URL}/episodeFile/{episode_file_id}?apikey={SONARR_API_KEY}"
        response = requests.delete(delete_url)
        if response.status_code == 200:
            print(f"Episode file for episode: {episode_name} from {series_name} deleted successfully from Sonarr.")
        else:
            print(f"Failed to delete episode file for episode: {episode_name} from {series_name}: {response.status_code}, {response.text}")
    else:
        print(f"Episode file not found for episode: {episode_name} from {series_name} or episode not downloaded/Previously deleted.")

def delete_movie_file(radarr_id, movie_name):
    delete_url = f"{RADARR_URL}/movie/{radarr_id}?deleteFiles=true&addImportExclusion=true&apikey={RADARR_API_KEY}"
    response = requests.delete(delete_url)
    if response.status_code == 200:
        print(f"Movie ID {movie_name} deleted successfully from Radarr.")
    else:
        print(f"Failed to delete movie ID {movie_name} from Radarr: {response.status_code}, {response.text}")

def main():
    # Update Blacklist with Favourites at start based on Env Variables
    watched_series = get_series_info(EMBY_USER_ID)
    if watched_series and IGNORE_FAVOURITES:
        for item in watched_series:
            if item['UserData']['IsFavorite'] and item['Type'] == 'Series' and HANDLE_TV:
                BLACKLISTED_PATHS.append(item['Path'])  # Add the path to blacklisted paths (should capture everything)
                print(f"Favorite Series: {item['Name']} and adding {item['Path']} to blacklisted paths")
                BLACKLISTED_TV_SHOWS.append(item['Name'])  # Add the Name to blacklisted Movies (Fall back for if path misses something)
                print(f"Favorite Series: {item['Name']} and adding to blacklisted TV Shows")
            elif item['UserData']['IsFavorite'] and item['Type'] == 'Movie' and HANDLE_MOVIES:
                BLACKLISTED_PATHS.append(item['Path'])  # Add the path to blacklisted paths (should capture everything)
                print(f"Favorite Movie: {item['Name']} and adding {item['Path']} to blacklisted paths")
                BLACKLISTED_MOVIES.append(item['Name'])  # Add the Name to blacklisted Movies (Fall back for if path misses something)
                print(f"Favorite Series: {item['Name']} and adding to blacklisted TV Shows")
                continue
    # Print statement for Handle TV = False
    if not HANDLE_TV:
        print("Handling of TV shows is disabled, Skipping to Movies.")
    # Logic for hadnling everything and calling the rest of the funcions
    #Gets list of watched items from emby
    watched_items = get_watched_items(EMBY_USER_ID)
    if watched_items:   # only acts on results from emby in watched items
        for item in watched_items:         #Loops through each item in watched items and applies the following logic
            if item['Type'] == 'Episode' and HANDLE_TV: #Checks if item type is an episode and if handle TV = True
                series_name = item['SeriesName']
                episode_name = item['Name']
                season_number = item['ParentIndexNumber']
                episode_number = item['IndexNumber']  
                item_info = f"{episode_name} from {series_name}"
                if item['UserData']['IsFavorite']: #Checks if episode is favourited in emby
                    print(f"Skipping favourite item: {item['Name']}")
                    continue
                if any(blacklisted_path in item['Path'] for blacklisted_path in BLACKLISTED_PATHS): # Checks if file path is in blacklisted Path
                    print(f"Skipping item in blacklisted path: {item['Name']}")
                    continue
                if series_name in BLACKLISTED_TV_SHOWS: # Checks if series name is blacklisted
                    print(f"Skipping blacklisted show: {series_name}")
                    continue  # Skip this iteration if the show is blacklisted
                # Fetch TVDB ID using series name
                tvdb_id = get_tvdb_id(series_name, item['Path'])
                if tvdb_id:
                    # Fetch Sonarr series ID using TVDB ID
                    series_id = get_series_id_by_tvdb(tvdb_id)
                    if series_id:
                        # Fetch episode info from Sonarr to get episode ID
                        episode_info = get_episode_info(series_id, season_number)
                        #print(episode_info)
                        for ep in episode_info:
                            if ep['seasonNumber'] == season_number and ep['episodeNumber'] == episode_number:
                                episode_id = ep['id']
                                episode_ids = [episode_id]
                                air_date_utc = datetime.strptime(ep['airDateUtc'], '%Y-%m-%dT%H:%M:%SZ')
                                do_not_delete = datetime.now() - timedelta(days=DAYS)
                                # Unmonitor this specific episode in Sonarr
                                unmonitor_episodes([episode_id])
                                print(f"Unmonitored episode: {item_info}")
                                if air_date_utc < do_not_delete and TV_DELETE:
                                    #delete the episode from Emby (OPTIONAL), Sonarr and file system
                                    delete_episode_file(series_id, season_number, episode_number, episode_name, series_name)
                                    if EMBY_DELETE:
                                        delete_item(item['Id'], item_info)
                                    if not EMBY_DELETE:
                                        print(f"Emby library update handled by Sonarr skipping Emby library delete for {series_name}: {episode_name} of Season{season_number}")
                                else:
                                    print(f"{series_name}: {episode_name} aired within the past {DAYS} days. Not Deleted")
                else:
                    print(f"TVDB ID not found for series '{series_name}'.")

            elif item['Type'] == 'Movie' and HANDLE_MOVIES:
                movie_name = item['Name']
                item_info = movie_name
                if item['UserData']['IsFavorite']:
                    print(f"Skipping favourite item: {item['Name']}")
                    continue
                if any(blacklisted_path in item['Path'] for blacklisted_path in BLACKLISTED_PATHS):
                    print(f"Skipping item in blacklisted path: {item['Name']}")
                    continue
                if movie_name in BLACKLISTED_MOVIES:
                    print(f"Skipping blacklisted Movie: {movie_name}")
                    continue  # Skip this iteration if the Movie is blacklisted
                elif movie_name not in BLACKLISTED_MOVIES:
                    # Use the movie name to fetch the TMDB ID directly
                    tmdb_id = get_tmdb_id(movie_name, item['Path'])
                    if tmdb_id:
                        movie_info = get_movie_info(tmdb_id, movie_name)
                        if movie_info:
                            radarr_id = movie_info['id']  # Assuming the first movie is the correct one
                            release_dates = [movie_info.get('inCinemas'), movie_info.get('physicalRelease'), movie_info.get('digitalRelease')]
                            release_dates = [datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ') for date in release_dates if date is not None]
                            if release_dates:  # Ensure there's at least one valid date
                                earliest_release_date = min(release_dates) if release_dates else None
                                Do_not_delete = datetime.now() - timedelta(days=DAYS)
                                # Unmonitor movies in Radarr
                                unmonitor_movies(radarr_id, movie_name) 
                                print(f"Unmonitored movie: {movie_name} with TMDB ID {tmdb_id}")
                                if earliest_release_date < Do_not_delete and MOVIE_DELETE:
                                    #delete the episode from Emby(OPTIONAL), Radarr and file system
                                    delete_movie_file(radarr_id, movie_name)
                                    if EMBY_DELETE:
                                        delete_item(item['Id'], item_info)
                                    if not EMBY_DELETE:
                                        print(f"Emby library update handled by Sonarr skipping Emby library delete for {movie_name}")
                                else:
                                    print(f"{movie_name} aired within the past {DAYS} days. Not Deleted")
                            else:
                                print(f"No valid release dates available for comparison: {movie_name}")
                    else:
                        print(f"TMDB ID not found for movie '{item_info}'.")
    else:
        print("No watched items found from Emby.")
    if not HANDLE_MOVIES:
        print("Handling of movies is disabled, Ending script.")

if __name__ == "__main__":
    main()
