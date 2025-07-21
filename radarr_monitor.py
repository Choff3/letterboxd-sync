import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(BASE_DIR, 'cache')
os.makedirs(CACHE_DIR, exist_ok=True)

PLEX_CACHE = os.path.join(CACHE_DIR, 'plex_cache.json')

def format_date(date=None):
    if not date:
        date = datetime.now()
    return date.strftime('%b %d %Y %I:%M%p').lower()

def radarr_monitor_add_from_plex_cache():
    """
    Read plex_cache.json, find movies marked as "Not in Library",
    request them in Radarr, and update the cache with results.
    """
    load_dotenv()
    
    # Get Radarr configuration from environment
    radarr_host = os.getenv('RADARR_HOST')
    radarr_api_key = os.getenv('RADARR_API_KEY')
    
    if not radarr_host or not radarr_api_key:
        print("Error: RADARR_HOST and RADARR_API_KEY must be set in environment variables")
        return
    
    print(f"[DEBUG] RADARR_HOST: {radarr_host}")
    print(f"[DEBUG] RADARR_API_KEY: {radarr_api_key[:6]}... (truncated)")
    
    # Load plex cache
    if not os.path.exists(PLEX_CACHE):
        print(f"Plex cache file '{PLEX_CACHE}' not found.")
        return
    
    with open(PLEX_CACHE, 'r') as f:
        plex_results = json.load(f)
    
    print(f"[DEBUG] Loaded {len(plex_results)} films from Plex cache.")
    
    # Filter for movies not in library
    movies_to_request = []
    for film in plex_results:
        if film.get('availability') == 'Not in Library':
            movies_to_request.append(film)
    
    print(f"[DEBUG] Found {len(movies_to_request)} movies to request in Radarr.")
    
    if not movies_to_request:
        print("No movies to request in Radarr.")
        return
    
    # Get root directory from Radarr
    try:
        root_dirs_resp = requests.get(f"{radarr_host}/api/v3/rootfolder", headers={"X-Api-Key": radarr_api_key}, timeout=30)
        root_dirs_resp.raise_for_status()
        root_dirs = root_dirs_resp.json()
        if not root_dirs:
            print("No root folders found in Radarr.")
            return
        root_folder = root_dirs[0]['path']
        print(f"[DEBUG] Using root folder: {root_folder}")
    except Exception as e:
        print(f"[ERROR] Could not get root folder from Radarr: {e}")
        return
    
    # Process each movie
    updated_count = 0
    for film in movies_to_request:
        name = film.get('film_name')
        tmdb_id = film.get('tmdb_id')
        
        if not tmdb_id:
            print(f"[DEBUG] Skipping '{name}' - no TMDB ID")
            continue
        
        print(f"[DEBUG] Processing: {name} (TMDB ID: {tmdb_id})")
        
        try:
            # Check if already in Radarr
            lookup_resp = requests.get(
                f"{radarr_host}/api/v3/movie/lookup/tmdb?tmdbId={tmdb_id}",
                headers={"X-Api-Key": radarr_api_key},
                timeout=30
            )
            lookup_resp.raise_for_status()
            lookup_data = lookup_resp.json()
            if not lookup_data:
                film['availability'] = f"Unable To Find on Radarr [{format_date()}]"
                print(f"✗ {name} not found in Radarr")
                updated_count += 1
                continue
            
            # Prepare add payload
            add_payload = {
                "title": lookup_data['title'],
                "qualityProfileId": 1,  # You may want to make this configurable
                "titleSlug": lookup_data['titleSlug'],
                "images": lookup_data.get('images', []),
                "tmdbId": lookup_data['tmdbId'],
                "year": lookup_data.get('year'),
                "rootFolderPath": root_folder,
                "monitored": True,
                "addOptions": {"searchForMovie": True}
            }
            
            add_resp = requests.post(
                f"{radarr_host}/api/v3/movie",
                headers={"X-Api-Key": radarr_api_key, "Content-Type": "application/json"},
                json=add_payload,
                timeout=30
            )
            
            if add_resp.status_code == 201:
                film['availability'] = f"Requested on [{format_date()}]"
                print(f"✓ Added {name} to Radarr requests")
                updated_count += 1
            elif add_resp.status_code == 400 and 'movie exists' in add_resp.text.lower():
                film['availability'] = f"Already Requested [{format_date()}]"
                print(f"ℹ {name} already requested in Radarr")
                updated_count += 1
            else:
                film['availability'] = f"Error: {add_resp.text} [{format_date()}]"
                print(f"✗ Error requesting {name}: {add_resp.text}")
                updated_count += 1
        except Exception as e:
            film['availability'] = f"Error: {str(e)} [{format_date()}]"
            print(f"✗ Unexpected error processing {name}: {e}")
            updated_count += 1
    
    # Save updated cache
    if updated_count > 0:
        with open(PLEX_CACHE, 'w') as f:
            json.dump(plex_results, f, indent=2)
        print(f"Updated Plex cache with {updated_count} new status entries.")
    else:
        print("No updates made to Plex cache.")

if __name__ == '__main__':
    radarr_monitor_add_from_plex_cache() 