import json
import sys
from plexapi.myplex import MyPlexAccount
from plexapi.server import PlexServer
import os
import requests

BASE_URL = "http://letterboxd-list-radarr.onrender.com"

def scrape_letterboxd(listUrl):
    try:
        list_url = BASE_URL+"/"+listUrl
        print("Grabbing "+list_url)
        return requests.get(list_url).json()
    except:
        sys.exit("Failed to connect to Letterboxd")

def plex_watchlist_sync(plex_host,plex_token, letterboxd_username):

    watchlist = scrape_letterboxd(letterboxd_username+"/watchlist/")

    server = PlexServer(plex_host, plex_token)

    plexAccount = MyPlexAccount(token=plex_token)

    plexWatchlist = plexAccount.watchlist()
    plexImdbs = []
    for film in plexWatchlist:
        imdbid = film.guids[0].id.split('imdb://',1)[1]
        plexImdbs.append(imdbid)

    for film in watchlist:
        try:
            plex_film = server.library.section('Movies').getGuid('imdb://'+film["imdb_id"])
            print("Found "+film["title"]+" on Plex server")
        except:
            print(film["title"]+" could not be found on Plex server")
            continue

        if film["imdb_id"] in plexImdbs:
            print(film["title"]+" is already on Plex watchlist")
        else:
            plexAccount.addToWatchlist(plex_film)
            print("Added "+film["title"]+" to Plex watchlist")

        # Remove from plexImdbs so we are left with films to be removed from Plex watchlist.
        try:
            plexImdbs.remove(film["imdb_id"])
        except ValueError as e:
            print("Error removing "+film["title"]+" from Plex watchlist")

    for imdbid in plexImdbs:
        plex_film = server.library.section('Movies').getGuid('imdb://'+imdbid)
        plexAccount.removeFromWatchlist(plex_film)
        print("Removed "+plex_film.title+" from Plex watchlist")

def plex_list_sync(plex_host,plex_token, playlists):

    server = PlexServer(plex_host, plex_token)

    for listUrl in playlists:

        letterboxdList = scrape_letterboxd(listUrl)
        
        plexFilms = []

        for film in letterboxdList:
            try:
                plex_film = server.library.section('Movies').getGuid('imdb://'+film["imdb_id"])
                plexFilms.append(plex_film)
                print("Found "+film["title"]+" on Plex server")
            except:
                print(film["title"]+" could not be found on Plex server")
                continue
        
        try:
            plexPlaylist = server.playlist(listUrl)
            plexPlaylist.delete()
            print("Recreating playlist")
        except:
            print("Creating new playlist")
        finally:
            server.createPlaylist(listUrl, plexFilms)

def main():

    plex_token = os.getenv('PLEX_TOKEN')
    plex_host = os.getenv('PLEX_HOST')
    letterboxd_username = os.getenv('LETTERBOXD_USERNAME')

    if plex_token != '' and plex_host != '':
        if letterboxd_username:
            plex_watchlist_sync(plex_host, plex_token, letterboxd_username)
        else:
            print("Skipping watchlist")
        try:
            playlists = json.loads(os.environ['PLAYLISTS'])
            plex_list_sync(plex_host, plex_token, playlists)
        except:
            print("Skipping playlists")
    else:
        print("Missing PLEX_TOKEN and/or PLEX_HOST")

if __name__ == "__main__":
    main()
