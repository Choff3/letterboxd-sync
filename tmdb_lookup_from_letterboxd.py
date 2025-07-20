import json
import os
import re
import requests
from dotenv import load_dotenv

load_dotenv()
TMDB_API_KEY = os.getenv('TMDB_API_KEY', '')
LETTERBOXD_CACHE = 'letterboxd_cache.json'
TMDB_CACHE = 'tmdb_cache.json'

def get_tmdb_id_from_api(title, year=None, api_key=None):
    if not api_key:
        print("[TMDB] No API key provided. Skipping TMDB lookup.")
        return None
    try:
        search_title = re.sub(r'[^\w\s]', '', title).strip()
        url = f"https://api.themoviedb.org/3/search/movie"
        params = {
            'api_key': api_key,
            'query': search_title,
            'language': 'en-US',
            'page': 1,
            'include_adult': False
        }
        if year and str(year).strip():
            params['year'] = year
        print(f"[TMDB] Searching for '{title}'" + (f" ({year})" if year and str(year).strip() else "") + "...")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        results = response.json().get('results', [])
        if results:
            print(f"[TMDB] Found TMDB ID {results[0]['id']} for '{title}'" + (f" ({year})" if year and str(year).strip() else ""))
            return str(results[0]['id'])
        else:
            print(f"[TMDB] No results for '{title}'" + (f" ({year})" if year and str(year).strip() else ""))
    except Exception as e:
        print(f"[TMDB] API error for '{title}': {e}")
    return None

def tmdb_lookup_all(letterboxd_cache='letterboxd_cache.json', tmdb_cache='tmdb_cache.json', api_key=None):
    if not api_key:
        load_dotenv()
        api_key = os.getenv('TMDB_API_KEY', '')
    if not os.path.exists(letterboxd_cache):
        print(f"Cache file '{letterboxd_cache}' not found.")
        return []
    with open(letterboxd_cache, 'r') as f:
        films = json.load(f)
    print(f"Loaded {len(films)} films from {letterboxd_cache}\n")
    tmdb_results = []
    for film in films:
        title = film.get('film_name')
        year = film.get('year')
        if not title or not title.strip():
            print(f"Skipping: missing title for film: {film}")
            continue
        tmdb_id = get_tmdb_id_from_api(title, year, api_key=api_key)
        tmdb_results.append({
            'film_name': title,
            'year': year,
            'tmdb_id': tmdb_id
        })
    with open(tmdb_cache, 'w') as f:
        json.dump(tmdb_results, f, indent=2)
    print(f"Saved TMDB results for {len(tmdb_results)} films to {tmdb_cache}")
    return tmdb_results

if __name__ == "__main__":
    tmdb_lookup_all() 