from plex_watchlist import *
import os
import requests

def main():

    # Scrape letterbox watchlist
    try:
        base_url = "http://letterboxd-list-radarr.onrender.com"
        letterboxd_username = os.getenv('LETTERBOXD_USERNAME')
        watchlist_url = base_url+"/"+letterboxd_username+"/watchlist/"
        watchlist = requests.get(watchlist_url).json()
        print("Successfully grabbed "+watchlist_url)
    except:
        print("Failed to connect to Letterboxd")

    # Add films to Plex watchlist
    plex_token = os.getenv('PLEX_TOKEN')
    plex_host = os.getenv('PLEX_HOST')
    if plex_token != '' and plex_host != '':
        plex_watchlist_sync(watchlist,plex_host,plex_token)
    else:
        print("Missing PLEX_TOKEN and/or PLEX_HOST")

if __name__ == "__main__":
    main()
