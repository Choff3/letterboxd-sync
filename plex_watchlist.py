from plexapi.myplex import MyPlexAccount
from plexapi.server import PlexServer
import os

def plex_watchlist_add(letterboxdFilms):

    missing_films = []

    TOKEN = os.getenv('PLEX_TOKEN')
    SERVER_URL = os.getenv('PLEX_HOST')

    server = PlexServer(SERVER_URL, TOKEN)

    plexAccount = MyPlexAccount(token=TOKEN)

    for film in letterboxdFilms:
        try:
            plex_film = server.library.section('Movies').getGuid('tmdb://'+film)
            plexAccount.addToWatchlist(plex_film)
        except:
            missing_films.append(film)

    return missing_films