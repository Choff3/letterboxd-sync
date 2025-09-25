from plexapi.myplex import MyPlexAccount
from plexapi.server import PlexServer
from plexapi.playlist import Playlist
import os
import requests

BASE_URL = "http://letterboxd-list-radarr.onrender.com"

def plex_watchlist_sync(plex_host,plex_token):

    # Scrape letterbox watchlist
    try:
        letterboxd_username = os.getenv('LETTERBOXD_USERNAME')
        watchlist_url = BASE_URL+"/"+letterboxd_username+"/watchlist/"
        watchlist = requests.get(watchlist_url).json()
        print("Successfully grabbed "+watchlist_url)
    except:
        print("Failed to connect to Letterboxd")
        return

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

def plex_list_sync(plex_host,plex_token):

    # LETTERBOXD_USERNAME='noodlesteddy'

    # lists = ["owencharlish/list/2025/"]

    # # Scrape letterbox list
    # try:
    #     letterboxd_username = LETTERBOXD_USERNAME#os.getenv('LETTERBOXD_USERNAME')
    #     list_url = BASE_URL+"/"+lists[0]
    #     list = requests.get(list_url).json()
    #     print("Successfully grabbed "+list_url)
    # except:
    #     print("Failed to connect to Letterboxd")
    #     return

    server = PlexServer(plex_host, plex_token)

    # plexPlaylists = server.playlists()

    # print(plexPlaylists[0].title)

    # TODO
    # Check if playlist exists
    # If it does, add items to Playlist
    # if it doesn't, create playlist with items.

    items = [server.library.section('Movies').getGuid('imdb://tt0110912')]

    print(items[0].title)

    Playlist.create(server,"poop",items=items)

    # plexAccount = Playlist(server, data)

    # plexPlaylist = plexAccount.watchlist()
    # plexImdbs = []
    # for film in plexPlaylist:
    #     imdbid = film.guids[0].id.split('imdb://',1)[1]
    #     plexImdbs.append(imdbid)

    # for film in list:
    #     try:
    #         plex_film = server.library.section('Movies').getGuid('imdb://'+film["imdb_id"])
    #         print("Found "+film["title"]+" on Plex server")
    #     except:
    #         print(film["title"]+" could not be found on Plex server")
    #         continue

    #     if film["imdb_id"] in plexImdbs:
    #         print(film["title"]+" is already on Plex watchlist")
    #     else:
    #         plexAccount.addToWatchlist(plex_film)
    #         print("Added "+film["title"]+" to Plex watchlist")

    #     # Remove from plexImdbs so we are left with films to be removed from Plex watchlist.
    #     try:
    #         plexImdbs.remove(film["imdb_id"])
    #     except ValueError as e:
    #         print("Error removing "+film["title"]+" from Plex watchlist")

    # for imdbid in plexImdbs:
    #     plex_film = server.library.section('Movies').getGuid('imdb://'+imdbid)
    #     plexAccount.removeFromWatchlist(plex_film)
    #     print("Removed "+plex_film+" from Plex watchlist")

def main():

    PLEX_TOKEN=''
    PLEX_HOST=''

    # Add films to Plex watchlist
    plex_token = PLEX_TOKEN#os.getenv('PLEX_TOKEN')
    plex_host = PLEX_HOST#os.getenv('PLEX_HOST')
    if plex_token != '' and plex_host != '':
        # plex_watchlist_sync(plex_host,plex_token)
        plex_list_sync(plex_host,plex_token)
    else:
        print("Missing PLEX_TOKEN and/or PLEX_HOST")

if __name__ == "__main__":
    main()
