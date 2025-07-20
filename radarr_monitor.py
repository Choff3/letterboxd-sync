import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

PLEX_CACHE = 'cache/plex_cache.json'

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
        root_response = requests.get(
            f"{radarr_host}/api/v3/rootfolder", 
            params={"apikey": radarr_api_key}, 
            timeout=30
        )
        root_response.raise_for_status()
        root_folders = root_response.json()
        
        if not root_folders:
            print("No root folders found in Radarr")
            return
            
        root_dir = root_folders[0]['path']
        print(f"[DEBUG] Using root directory: {root_dir}")
        
    except requests.RequestException as e:
        print(f"Error connecting to Radarr: {e}")
        return
    except Exception as e:
        print(f"Error getting root folder: {e}")
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
            # Look up movie by TMDB ID
            movie_response = requests.get(
                f"{radarr_host}/api/v3/movie/lookup/tmdb?tmdbId={tmdb_id}", 
                params={"apikey": radarr_api_key}, 
                timeout=30
            )
            movie_response.raise_for_status()
            movie = movie_response.json()
            
            if not movie:
                # Movie not found in Radarr
                date_checked = format_date()
                film['availability'] = f"Unable To Find on Radarr [{date_checked}]"
                print(f"✗ {name} not found in Radarr")
                updated_count += 1
                continue
            
            # Configure movie settings
            movie["QualityProfileId"] = 1
            movie["rootFolderPath"] = root_dir
            movie["monitored"] = True
            movie["searchOnAdd"] = True
            
            # Add movie to Radarr
            add_response = requests.post(
                f"{radarr_host}/api/v3/movie", 
                params={"apikey": radarr_api_key}, 
                json=movie,
                timeout=30
            )
            add_response.raise_for_status()
            
            # Update cache with success
            date_requested = format_date()
            film['availability'] = f"Requested on [{date_requested}]"
            print(f"✓ Added {name} to Radarr monitoring")
            updated_count += 1
            
        except requests.RequestException as e:
            # Network/API error
            date_error = format_date()
            film['availability'] = f"Error: {str(e)} [{date_error}]"
            print(f"✗ Error requesting {name}: {e}")
            updated_count += 1
        except Exception as e:
            # Unexpected error
            date_error = format_date()
            film['availability'] = f"Error: {str(e)} [{date_error}]"
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