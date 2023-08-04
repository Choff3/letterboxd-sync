from pyarr import RadarrAPI
import os
from dotenv import load_dotenv

def radarr_monitor_add(missing_films):

    # Set Host URL and API-Key

    host_url = os.getenv('RADARR_HOST')

    # You can find your API key in Settings > General.

    api_key = os.getenv('RADARR_TOKEN')

    # Instantiate Radarr Object

    radarr = RadarrAPI(host_url, api_key)

    # Get and print TV Shows

    # print(radarr.get_movie())