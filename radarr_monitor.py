import requests
import os

def radarr_monitor_add(radarr_films, host_url, api_key):
    try:
        # Get root directory
        root_response = requests.get(host_url+'/api/v3/rootfolder', params={"apikey": api_key}, timeout=30)
        root_response.raise_for_status()
        root_folders = root_response.json()
        
        if not root_folders:
            print("No root folders found in Radarr")
            return
            
        root_dir = root_folders[0]['path']
        print(f"Using root directory: {root_dir}")
        
    except requests.RequestException as e:
        print(f"Error connecting to Radarr: {e}")
        return
    except Exception as e:
        print(f"Error getting root folder: {e}")
        return

    for tmdbid in radarr_films:
        try:
            # Look up movie by TMDB ID
            movie_response = requests.get(
                host_url+'/api/v3/movie/lookup/tmdb?tmdbId='+tmdbid, 
                params={"apikey": api_key}, 
                timeout=30
            )
            movie_response.raise_for_status()
            movie = movie_response.json()

            # Configure movie settings
            movie["QualityProfileId"] = 1
            movie["rootFolderPath"] = root_dir
            movie["monitored"] = True
            movie["searchOnAdd"] = True

            # Add movie to Radarr
            add_response = requests.post(
                host_url+'/api/v3/movie', 
                params={"apikey": api_key}, 
                json=movie,
                timeout=30
            )
            add_response.raise_for_status()
            print(f"Added tmdb://{tmdbid} to Radarr monitoring")
            
        except requests.RequestException as e:
            print(f"Error adding tmdb://{tmdbid} to Radarr: {e}")
        except Exception as e:
            print(f"Unexpected error processing tmdb://{tmdbid}: {e}")