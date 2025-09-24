from plexapi.myplex import MyPlexAccount
from plexapi.server import PlexServer
import os

def plex_watchlist_sync(letterboxdFilms,plex_host,plex_token):

    server = PlexServer(plex_host, plex_token)

    plexAccount = MyPlexAccount(token=plex_token)

    plexWatchlist = plexAccount.watchlist()
    plexImdbs = []
    for film in plexWatchlist:
        imdbid = film.guids[0].id.split('imdb://',1)[1]
        plexImdbs.append(imdbid)

    for film in letterboxdFilms:
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
            print("Error removing "+film["imdb_id"]+" from Plex watchlist")

    for imdbid in plexImdbs:
        plex_film = server.library.section('Movies').getGuid('imdb://'+imdbid)
        plexAccount.removeFromWatchlist(plex_film)
        print("Removed "+plex_film+" from Plex watchlist")