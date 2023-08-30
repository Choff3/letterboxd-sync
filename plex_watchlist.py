from plexapi.myplex import MyPlexAccount
from plexapi.server import PlexServer
import os

def plex_watchlist_add(letterboxdFilms,plex_host,plex_token):

    missing_films = []

    server = PlexServer(plex_host, plex_token)

    plexAccount = MyPlexAccount(token=plex_token)

    for film in letterboxdFilms:
        try:
            plex_film = server.library.section('Movies').getGuid('tmdb://'+film)
        except:
            print("tmdb://"+film+" not available in Plex")
            missing_films.append(film)
            continue
        try:
            plexAccount.addToWatchlist(plex_film)
            print("Added "+plex_film.guids[1].id+" to Plex watchlist")
        except:
            print("tmdb://"+film+" already on watchlist")
            continue

    plexWatchlist = plexAccount.watchlist()

    for film in plexWatchlist:
        tmdbid = film.guids[1].id.split('tmdb://',1)[1]
        if tmdbid not in letterboxdFilms:
            plex_film = server.library.section('Movies').getGuid('tmdb://'+tmdbid)
            plexAccount.removeFromWatchlist(plex_film)
            print("Removed tmdb://"+tmdbid+" from Plex watchlist")

    return missing_films