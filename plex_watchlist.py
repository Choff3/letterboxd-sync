from plexapi.myplex import MyPlexAccount
from plexapi.server import PlexServer
import os

def plex_watchlist_add(letterboxdFilms, plex_host, plex_token):
    missing_films = []

    try:
        server = PlexServer(plex_host, plex_token)
        plexAccount = MyPlexAccount(token=plex_token)
    except Exception as e:
        print(f"Error connecting to Plex: {e}")
        return letterboxdFilms

    for film in letterboxdFilms:
        try:
            plex_film = server.library.section('Movies').getGuid('tmdb://'+film)
        except Exception:
            print(f"tmdb://{film} not available in Plex")
            missing_films.append(film)
            continue
        
        try:
            plexAccount.addToWatchlist(plex_film)
            print(f"Added {plex_film.guids[1].id} to Plex watchlist")
        except Exception:
            print(f"tmdb://{film} already on watchlist")
            continue

    try:
        plexWatchlist = plexAccount.watchlist()

        for film in plexWatchlist:
            try:
                tmdbid = film.guids[1].id.split('tmdb://',1)[1]
                if tmdbid not in letterboxdFilms:
                    plex_film = server.library.section('Movies').getGuid('tmdb://'+tmdbid)
                    plexAccount.removeFromWatchlist(plex_film)
                    print(f"Removed tmdb://{tmdbid} from Plex watchlist")
            except Exception as e:
                print(f"Error processing watchlist item: {e}")
                continue
    except Exception as e:
        print(f"Error accessing Plex watchlist: {e}")

    return missing_films