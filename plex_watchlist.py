from plexapi.myplex import MyPlexAccount
from plexapi.server import PlexServer
import os
import json

CACHE_FILE = 'film_cache.json'

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            try:
                return json.load(f)
            except Exception:
                return {}
    return {}

def save_cache(cache):
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=2)

def plex_watchlist_add(letterboxdFilms, plex_host, plex_token):
    missing_films = []
    cache = load_cache()
    updated = False
    try:
        server = PlexServer(plex_host, plex_token)
        plexAccount = MyPlexAccount(token=plex_token)
    except Exception as e:
        print(f"Error connecting to Plex: {e}")
        return letterboxdFilms

    for film in letterboxdFilms:
        film_key = None
        # Find the film_key in cache by tmdb_id
        for k, v in cache.items():
            if v.get('tmdb_id') == film:
                film_key = k
                break
        try:
            plex_film = server.library.section('Movies').getGuid('tmdb://'+film)
        except Exception:
            print(f"tmdb://{film} not available in Plex")
            missing_films.append(film)
            if film_key:
                cache[film_key]['added_to_plex_watchlist'] = 'not_in_plex'
                updated = True
            continue
        try:
            plexAccount.addToWatchlist(plex_film)
            print(f"Added {plex_film.guids[1].id} to Plex watchlist")
            if film_key:
                cache[film_key]['added_to_plex_watchlist'] = 'success'
                updated = True
        except Exception:
            print(f"tmdb://{film} already on watchlist")
            if film_key:
                cache[film_key]['added_to_plex_watchlist'] = 'already_on_watchlist'
                updated = True
            continue
    # Ensure all films in cache have the field
    for k, v in cache.items():
        if 'added_to_plex_watchlist' not in v:
            cache[k]['added_to_plex_watchlist'] = 'not_attempted'
            updated = True
    if updated:
        save_cache(cache)
    return missing_films