import json
import os
from plexapi.server import PlexServer
from datetime import datetime

TMDB_CACHE = 'cache/tmdb_cache.json'
PLEX_CACHE = 'cache/plex_cache.json'

def format_date(date=None):
    if not date:
        date = datetime.now()
    return date.strftime('%b %d %Y').lower()

def plex_watchlist_add_from_tmdb_cache(plex_host, plex_token):
    print(f"[DEBUG] PLEX_HOST: {plex_host}")
    print(f"[DEBUG] PLEX_TOKEN: {plex_token[:6]}... (truncated)")
    print(f"[DEBUG] Loading TMDB cache from: {TMDB_CACHE}")
    if not os.path.exists(TMDB_CACHE):
        print(f"TMDB cache file '{TMDB_CACHE}' not found.")
        return []
    with open(TMDB_CACHE, 'r') as f:
        films = json.load(f)
    print(f"[DEBUG] Loaded {len(films)} films from TMDB cache.")
    try:
        print(f"[DEBUG] Attempting to connect to Plex server at {plex_host}...")
        server = PlexServer(plex_host, plex_token)
        print(f"[DEBUG] Connected to Plex server: {server.friendlyName}")
        print(f"[DEBUG] Note: Using managed user access - will check library availability only")
    except Exception as e:
        print(f"[ERROR] Error connecting to Plex: {e}")
        return []
    
    plex_results = []
    for film in films:
        name = film.get('film_name')
        tmdb_id = film.get('tmdb_id')
        print(f"[DEBUG] Processing film: {name} (TMDB ID: {tmdb_id})")
        if not tmdb_id:
            plex_results.append({
                'film_name': name,
                'tmdb_id': tmdb_id,
                'date_added': '',
                'availability': 'Not Found'
            })
            continue
        try:
            print(f"[DEBUG] Looking up film in Plex library: tmdb://{tmdb_id}")
            plex_film = server.library.section('Movies').getGuid('tmdb://' + tmdb_id)
            date_checked = format_date()
            plex_results.append({
                'film_name': name,
                'tmdb_id': tmdb_id,
                'date_added': date_checked,
                'availability': 'Available in Library'
            })
            print(f"✓ {name} (TMDB {tmdb_id}) found in Plex library.")
        except Exception as e:
            print(f"[DEBUG] Film not found in Plex library: {e}")
            date_checked = format_date()
            plex_results.append({
                'film_name': name,
                'tmdb_id': tmdb_id,
                'date_added': '',
                'availability': f'Not in Library (checked {date_checked})'
            })
            print(f"✗ {name} (TMDB {tmdb_id}) not found in Plex library.")
    
    with open(PLEX_CACHE, 'w') as f:
        json.dump(plex_results, f, indent=2)
    print(f"Saved Plex results for {len(plex_results)} films to {PLEX_CACHE}")
    return plex_results