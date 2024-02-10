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

#tvdb/tmdb
TVDB_API_KEY = 'TVDB_API_KEY'
TMDB_API_KEY = 'TMDB_API_KEY'
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
            # Assuming you want the first result
            first_result = results[0]
            return first_result.get('id')
    else:
        print(f"Error searching TMDB for {movie_name}: {response.status_code}")
    return None

def get_tvdb_token(api_key):
    url = 'https://api.thetvdb.com/login'
    headers = {'Content-Type': 'application/json'}
    data = {'apikey': api_key}
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        return response.json().get('token')
    print(f"Failed to obtain TVDB token: {response.status_code}, {response.text}")
    return None

def get_tvdb_id(series_name):
    api_key = TVDB_API_KEY  # Use the global API key
    token = get_tvdb_token(api_key)
    if not token:
        print("Failed to get TVDB token.")
        return None

    search_url = 'https://api.thetvdb.com/search/series'
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json'
    }
    params = {'name': series_name}
    response = requests.get(search_url, headers=headers, params=params)

    if response.status_code == 200:
        results = response.json().get('data', [])
        if results:
            return results[0].get('id')
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

@app.route('/webhook/emby', methods=['POST'])
def emby_webhook():
    data = request.json
    if not data or 'Items' not in data:
        return 'Invalid data', 400

    for item in data['Items']:
        if item['Type'] == 'Episode' and item.get('SeriesName') not in BLACKLISTED_TV_SHOWS:
            # Fetch the TVDB ID using the series name
            tvdb_id = get_tvdb_id(item['SeriesName'], TVDB_API_KEY)
            if tvdb_id:
                series_id = get_series_id_by_tvdb(tvdb_id)
                if series_id:
                    episode_info = get_episode_info(series_id, item['ParentIndexNumber'])
                    if episode_info:
                        episode_ids = [ep['id'] for ep in episode_info if ep['episodeNumber'] == item['IndexNumber']]
                        if episode_ids:
                            unmonitor_episodes(episode_ids, False)
                            for episode_id in episode_ids:
                                delete_episode_file(episode_id)
                                print(f"Webhook processed episode: {item['Name']} from series: {item['SeriesName']} with TVDB ID {tvdb_id}")
            else:
                print(f"TVDB ID not found for series '{item['SeriesName']}'.")

        elif item['Type'] == 'Movie' and item.get('Name') not in BLACKLISTED_MOVIES:
            # Fetch the TMDB ID using the movie name
            tmdb_id = get_tmdb_id(item['Name'])
            if tmdb_id:
                movie_info = get_movie_info_by_tmdb(tmdb_id)
                if movie_info:
                    radarr_id = movie_info[0]['id']  # Assuming the first movie is the correct one
                    unmonitor_movies(radarr_id, False)
                    delete_movie(radarr_id, delete_files=False, add_import_exclusion=False)
                    print(f"Webhook processed movie: {item['Name']} with TMDB ID {tmdb_id}")
            else:
                print(f"TMDB ID not found for movie '{item['Name']}'.")

    return 'Webhook processed', 200

def main():
    watched_items = get_watched_items(EMBY_USER_ID)
    if watched_items:
        for item in watched_items:
            if item['Type'] == 'Episode' and item.get('SeriesName') not in BLACKLISTED_TV_SHOWS:
                # Use the series name to fetch the TVDB ID directly
                tvdb_id = get_tvdb_id(item['SeriesName'])
                if tvdb_id:
                    # Assuming get_series_id_by_tvdb returns the Sonarr series ID using the TVDB ID
                    series_id = get_series_id_by_tvdb(tvdb_id)
                    if series_id:
                        episode_info = get_episode_info(series_id, item['ParentIndexNumber'])
                        if episode_info:
                            episode_ids = [ep['id'] for ep in episode_info if ep['episodeNumber'] == item['IndexNumber']]
                            if episode_ids:
                                unmonitor_episodes(episode_ids, False)
                                for episode_id in episode_ids:
                                    delete_episode_file(episode_id)
                                    print(f"Processed episode: {item['Name']} from series: {item['SeriesName']} with TVDB ID {tvdb_id}")
                else:
                    print(f"TVDB ID not found for series '{item['SeriesName']}'.")

            elif item['Type'] == 'Movie' and item.get('Name') not in BLACKLISTED_MOVIES:
                # Use the movie name to fetch the TMDB ID directly
                tmdb_id = get_tmdb_id(item['Name'])
                if tmdb_id:
                    # Assuming get_movie_info_by_tmdb returns the Radarr movie info using the TMDB ID
                    movie_info = get_movie_info_by_tmdb(tmdb_id)
                    if movie_info:
                        radarr_id = movie_info['id']  # Assuming the first movie is the correct one
                        unmonitor_movies(radarr_id, False)
                        delete_movie(radarr_id, delete_files=False, add_import_exclusion=False)
                        print(f"Processed movie: {item['Name']} with TMDB ID {tmdb_id}")
                else:
                    print(f"TMDB ID not found for movie '{item['Name']}'.")

    else:
        print("No watched items found from Emby.")

    # Uncomment the line below if you are running this as a standalone script without needing Flask's web server capabilities.
    # app.run(debug=True, port=5000)

if __name__ == "__main__":
    main()