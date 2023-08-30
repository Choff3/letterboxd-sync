from list_scraper import *
from plex_watchlist import *
from radarr_monitor import *
import os

def main():

    # Scrape letterbox watchlist
    letterboxd_username = os.getenv('LETTERBOXD_USERNAME')
    list_url = "https://letterboxd.com/"+letterboxd_username+"/watchlist/"
    list_url.split('/')[-3]
    films = scrape_list(list_url)

    # Add films to Plex watchlist
    plex_token = os.getenv('PLEX_TOKEN')
    plex_host = os.getenv('PLEX_HOST')
    if plex_token != '' and plex_host != '':
        radarr_films = plex_watchlist_add(films,plex_host,plex_token)
    else:
        print("Skipping Plex")
        radarr_films = films

    # Add films to Radarr
    radarr_host = os.getenv('RADARR_HOST')
    radarr_api = os.getenv('RADARR_TOKEN')
    if radarr_api == '' or radarr_host == '' or not radarr_films:
        print("Skipping Radarr")
    else:
        radarr_monitor_add(radarr_films,radarr_host,radarr_api)

if __name__ == "__main__":
    main()
