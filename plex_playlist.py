import os
import json
import random
from datetime import datetime
from plexapi.server import PlexServer
from dotenv import load_dotenv

TMDB_CACHE = 'cache/tmdb_cache.json'
PLEX_CACHE = 'cache/plex_cache.json'
PLAYLIST_NAME = 'Letterboxd Watchlist'

load_dotenv()

def format_date(date=None):
    if not date:
        date = datetime.now()
    return date.strftime('%b %d %Y').lower()

def main():
    plex_host = os.getenv('PLEX_HOST')
    plex_token = os.getenv('PLEX_TOKEN')
    print(f"[DEBUG] PLEX_HOST: {plex_host}")
    print(f"[DEBUG] PLEX_TOKEN: {plex_token[:6]}... (truncated)")

    # Load TMDB cache
    if not os.path.exists(TMDB_CACHE):
        print(f"TMDB cache file '{TMDB_CACHE}' not found.")
        return
    with open(TMDB_CACHE, 'r') as f:
        films = json.load(f)
    print(f"[DEBUG] Loaded {len(films)} films from TMDB cache.")

    try:
        server = PlexServer(plex_host, plex_token)
        print(f"[DEBUG] Connected to Plex server: {server.friendlyName}")
        movies_section = server.library.section('Movies')
    except Exception as e:
        print(f"[ERROR] {e}")
        return

    plex_results = []
    items_to_add = []
    for film in films:
        name = film.get('film_name')
        tmdb_id = film.get('tmdb_id')
        year = film.get('film_year')
        print(f"[DEBUG] Processing film: {name} (TMDB ID: {tmdb_id}, Year: {year})")
        if not tmdb_id:
            plex_results.append({
                'film_name': name,
                'tmdb_id': tmdb_id,
                'date_added': '',
                'availability': 'Not Found'
            })
            continue
        # Search by title and optionally year
        try:
            if year:
                results = movies_section.search(title=name, year=year)
            else:
                results = movies_section.search(title=name)
            if results:
                print(f"[DEBUG] Found {len(results)} result(s) for '{name}'. Adding to playlist.")
                items_to_add.append(results[0])
                date_added = format_date()
                plex_results.append({
                    'film_name': name,
                    'tmdb_id': tmdb_id,
                    'date_added': date_added,
                    'availability': 'Available in Library'
                })
            else:
                print(f"[DEBUG] No results found for '{name}'.")
                plex_results.append({
                    'film_name': name,
                    'tmdb_id': tmdb_id,
                    'date_added': '',
                    'availability': 'Not in Library'
                })
        except Exception as e:
            print(f"[ERROR] Searching for '{name}': {e}")
            plex_results.append({
                'film_name': name,
                'tmdb_id': tmdb_id,
                'date_added': '',
                'availability': f'Error: {e}'
            })

    # Try to find existing playlist
    playlist = None
    for pl in server.playlists():
        if pl.title == PLAYLIST_NAME:
            playlist = pl
            print(f"[DEBUG] Found existing playlist: {PLAYLIST_NAME}")
            break

    # Create or update playlist only if there are items to add
    if items_to_add:
        # Shuffle the items before adding to playlist
        random.shuffle(items_to_add)
        print(f"[DEBUG] Shuffled {len(items_to_add)} items for playlist.")
        
        if not playlist:
            print(f"[DEBUG] Creating new playlist: {PLAYLIST_NAME}")
            playlist = server.createPlaylist(PLAYLIST_NAME, items=items_to_add)
        else:
            try:
                # Simple approach: always recreate playlist for now
                # This ensures it always matches the current TMDB cache exactly
                playlist.delete()
                playlist = server.createPlaylist(PLAYLIST_NAME, items=items_to_add)
                print(f"[DEBUG] Recreated playlist '{PLAYLIST_NAME}' with {len(items_to_add)} shuffled items.")
                print(f"[DEBUG] Note: Using recreation approach to ensure exact sync with TMDB cache.")
                    
            except Exception as e:
                print(f"[ERROR] Updating playlist: {e}")
                # Fallback: recreate playlist
                try:
                    playlist.delete()
                    playlist = server.createPlaylist(PLAYLIST_NAME, items=items_to_add)
                    print(f"[DEBUG] Fallback: recreated playlist '{PLAYLIST_NAME}' with {len(items_to_add)} items.")
                except Exception as e2:
                    print(f"[ERROR] Fallback also failed: {e2}")
    else:
        # If no items to add, delete the playlist if it exists
        if playlist:
            try:
                playlist.delete()
                print(f"[DEBUG] Deleted playlist '{PLAYLIST_NAME}' - no movies found in TMDB cache.")
            except Exception as e:
                print(f"[ERROR] Deleting playlist: {e}")
        else:
            print(f"[DEBUG] No items to add to playlist. Playlist not created.")

    # Write results to plex_cache.json
    with open(PLEX_CACHE, 'w') as f:
        json.dump(plex_results, f, indent=2)
    print(f"Saved Plex results for {len(plex_results)} films to {PLEX_CACHE}")

if __name__ == '__main__':
    main() 