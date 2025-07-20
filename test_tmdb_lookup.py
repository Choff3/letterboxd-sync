import os
import re
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TMDB_API_KEY = os.getenv('TMDB_API_KEY', '')

def get_tmdb_id_from_api(title, year=None):
    if not TMDB_API_KEY:
        print("[TMDB] No API key provided. Skipping TMDB lookup.")
        return None
    try:
        search_title = re.sub(r'[^\w\s]', '', title).strip()
        url = f"https://api.themoviedb.org/3/search/movie"
        params = {
            'api_key': TMDB_API_KEY,
            'query': search_title,
            'language': 'en-US',
            'page': 1,
            'include_adult': False
        }
        if year:
            params['year'] = year
        print(f"[TMDB] Searching for '{title}' ({year})...")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        results = response.json().get('results', [])
        if results:
            print(f"[TMDB] Found TMDB ID {results[0]['id']} for '{title}' ({year})")
            return str(results[0]['id'])
        else:
            print(f"[TMDB] No results for '{title}' ({year})")
    except Exception as e:
        print(f"[TMDB] API error for '{title}': {e}")
    return None

def main():
    title = "The Girl with the Dragon Tattoo"
    year = "2011"
    tmdb_id = get_tmdb_id_from_api(title, year)
    if tmdb_id:
        print(f"TMDB ID for '{title} ({year})': {tmdb_id}")
    else:
        print(f"No TMDB ID found for '{title} ({year})'")

if __name__ == "__main__":
    main() 