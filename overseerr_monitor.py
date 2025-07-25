import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(BASE_DIR, 'cache')
os.makedirs(CACHE_DIR, exist_ok=True)

PLEX_CACHE = os.path.join(CACHE_DIR, 'plex_watchlist_cache.json')

def format_date(date=None):
    if not date:
        date = datetime.now()
    return date.strftime('%b %d %Y %I:%M%p').lower()

def overseerr_monitor_add_from_plex_cache():
    """
    Read plex_watchlist_cache.json, find movies marked as "Not in Library",
    request them in Overseerr, and update the cache with results.
    """
    load_dotenv()
    
    # Get Overseerr configuration from environment
    overseerr_host = os.getenv('OVERSEERR_HOST')
    overseerr_api_key = os.getenv('OVERSEERR_API_KEY')  # Using OVERSEERR_API_KEY from your .env
    
    if not overseerr_host or not overseerr_api_key:
        print("Error: OVERSEERR_HOST and OVERSEERR_API_KEY must be set in environment variables")
        print("Please add OVERSEERR_HOST=http://your_overseerr_ip:port to your .env file")
        return
    
    print(f"[DEBUG] OVERSEERR_HOST: {overseerr_host}")
    print(f"[DEBUG] OVERSEERR_API_KEY: {overseerr_api_key[:6]}... (truncated)")
    
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
    
    print(f"[DEBUG] Found {len(movies_to_request)} movies to request in Overseerr.")
    
    if not movies_to_request:
        print("No movies to request in Overseerr.")
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
            # Request movie via Overseerr API
            request_data = {
                "mediaType": "movie",
                "mediaId": int(tmdb_id),
                "is4k": False  # Set to True if you want 4K requests
            }
            
            request_response = requests.post(
                f"{overseerr_host}/api/v1/request", 
                headers={
                    "X-Api-Key": overseerr_api_key,
                    "Content-Type": "application/json"
                },
                json=request_data,
                timeout=30
            )
            
            if request_response.status_code == 201:
                # Successfully requested
                date_requested = format_date()
                film['availability'] = f"Requested on [{date_requested}]"
                print(f"✓ Added {name} to Overseerr requests")
                updated_count += 1
                
            elif request_response.status_code == 409:
                # Already requested
                date_checked = format_date()
                film['availability'] = f"Already Requested [{date_checked}]"
                print(f"ℹ {name} already requested in Overseerr")
                updated_count += 1
                
            elif request_response.status_code == 404:
                # Movie not found
                date_checked = format_date()
                film['availability'] = f"Unable To Find on Overseerr [{date_checked}]"
                print(f"✗ {name} not found in Overseerr")
                updated_count += 1
                
            else:
                # Other error
                error_msg = request_response.text if request_response.text else f"HTTP {request_response.status_code}"
                date_error = format_date()
                film['availability'] = f"Error: {error_msg} [{date_error}]"
                print(f"✗ Error requesting {name}: {error_msg}")
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
    overseerr_monitor_add_from_plex_cache() 