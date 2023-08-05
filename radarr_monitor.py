from pyarr import RadarrAPI
import os

def radarr_monitor_add(missing_films):

    # Set Host URL and API-Key

    host_url = os.getenv('RADARR_HOST')

    # You can find your API key in Settings > General.

    api_key = os.getenv('RADARR_TOKEN')

    # Instantiate Radarr Object

    radarr = RadarrAPI(host_url, api_key)

    quality_profile_num = 0
    quality_profile = radarr.get_quality_profile()[quality_profile_num]['id']

    root_dir_num = 0
    root_dir = radarr.get_root_folder()[root_dir_num]['path']

    for tmdbid in missing_films:
        film = radarr.lookup_movie_by_tmdb_id(tmdbid)
        radarr.add_movie(film,root_dir,quality_profile)