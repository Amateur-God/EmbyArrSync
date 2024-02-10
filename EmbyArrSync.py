from datetime import datetime, timedelta
import requests

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

def get_watched_items(user_id):
    url = f"{EMBY_URL}/Users/{user_id}/Items/Latest"
    params = {
        'IsFolder': 'false',
        'IsPlayed': 'true',
        'GroupItems': 'false',
        'EnableImages': 'false',
        'EnableUserData': 'false',
        'Limit': '10000',
        'api_key': EMBY_API_KEY
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        watched_items = response.json()
        return watched_items
    else:
        print("Error fetching watched items from Emby")
        return None

def get_tmdb_id(movie_name):
    search_url = f'https://api.themoviedb.org/3/search/movie'
    params = {
        'api_key': TMDB_API_KEY,
        'query': movie_name
    }
    response = requests.get(search_url, params=params)
    if response.status_code == 200:
        results = response.json().get('results', [])
        if results:
            # Assuming first result is correct
            first_result = results[0]
            return first_result.get('id')
    else:
        print(f"Error searching TMDB for {movie_name}: {response.status_code}")
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

def get_tvdb_id(series_name):
    search_url = f"https://api4.thetvdb.com/v4/search?query={series_name}"
    headers = {
        'Authorization': f'Bearer {TVDB_TOKEN}',
        'Content-Type': 'application/json'
    }
    params = {'query': series_name, 'type': 'series'}
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
            return series_info[0]['id']  # Assuming the first series is the correct one (it should be if TVDBID is correct)
    else:
        print(f"Error fetching series by TVDB ID: {response.status_code}")
    return None

def unmonitor_episodes(episode_ids, monitored):
    url = f"{SONARR_URL}/episode/monitor"
    api_key_param = f"apikey={SONARR_API_KEY}"
    if "?" in url:
        url += f"&{api_key_param}"
    else:
        url += f"?{api_key_param}"
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
    }
    payload = {
        'episodeIds': episode_ids,
        'monitored': False
    }
    response = requests.put(url, headers=headers, json=payload)
    if response.status_code == 200:
        print("Monitoring status changed successfully.")
    if response.status_code == 202:
        print("Monitoring status Queued.")
    else:
        print(f"Error changing monitoring status: {response.status_code}")

def get_movie_info_by_tmdb(tmdb_id):
    url = f"{RADARR_URL}/movie/lookup/tmdb/{tmdb_id}?apikey={RADARR_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        movie_info = response.json()
        if isinstance(movie_info, list) and len(movie_info) > 0:
            # Assuming the first movie in the list is the one you want
            return movie_info[0]
        else:
            print("No movies found for TMDB ID:", tmdb_id)
            return None
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
    if response.status_code == 202:
        print("Monitoring status Queued.")
    else:
        print(f"Error updating monitoring status for movie ID {radarr_id}: {response.status_code}")

def delete_item(item_id):
    url = f"{EMBY_URL}/Items?{item_id}&api_key={EMBY_API_KEY}"
    response = requests.delete(url)
    if response.status_code == 204:
        print(f"Item {item_id} deleted successfully from Emby.")
    else:
        print(f"Failed to delete item {item_id} from Emby: {response.status_code}, {response.text}")

def main():
    two_weeks_ago = datetime.utcnow() - timedelta(days=14)
    watched_items = get_watched_items(EMBY_USER_ID)
    if watched_items:
        for item in watched_items:
            if item['Type'] == 'Episode' and item.get('SeriesName') not in BLACKLISTED_TV_SHOWS:
                series_name = item['SeriesName']
                season_number = item['ParentIndexNumber']
                episode_number = item['IndexNumber']
                
                # Fetch TVDB ID using series name
                tvdb_id = get_tvdb_id(series_name)
                if tvdb_id:
                    # Fetch Sonarr series ID using TVDB ID
                    series_id = get_series_id_by_tvdb(tvdb_id)
                    if series_id:
                        # Fetch episode info from Sonarr to get episode ID
                        episode_info = get_episode_info(series_id, season_number)
                        for ep in episode_info:
                            if ep['seasonNumber'] == season_number and ep['episodeNumber'] == episode_number:
                                air_date_utc = datetime.strptime(ep['airDateUtc'], '%Y-%m-%dT%H:%M:%SZ')
                                if air_date_utc < two_weeks_ago:
                                    # Unmonitor this specific episode in Sonarr
                                    unmonitor_episodes([ep['id']], False)
                                    print(f"Unmonitored episode: {ep['title']} from series: {series_name}")
                    
                                    # delete the episode from Emby and file system
                                    delete_item(item['Id'])
                else:
                    print(f"TVDB ID not found for series '{series_name}'.")
                    

            elif item['Type'] == 'Movie' and item.get('Name') not in BLACKLISTED_MOVIES:
                # Use the movie name to fetch the TMDB ID directly
                tmdb_id = get_tmdb_id(item['Name'])
                if tmdb_id:
                    movie_info = get_movie_info_by_tmdb(tmdb_id)
                    if movie_info:
                        radarr_id = movie_info['id']  # Assuming the first movie is the correct one
                        # Unmonitor movies in Radarr
                        unmonitor_movies(radarr_id, False)
                        print(f"Unmonitored movie: {item['Name']} with TMDB ID {tmdb_id}")
                        #delete the episode from Emby and file system
                        delete_item(item['Id'])
                else:
                    print(f"TMDB ID not found for movie '{item['Name']}'.")

    else:
        print("No watched items found from Emby.")

if __name__ == "__main__":
    main()
