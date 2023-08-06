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
            plexAccount.addToWatchlist(plex_film)
        except:
            missing_films.append(film)

    return missing_films