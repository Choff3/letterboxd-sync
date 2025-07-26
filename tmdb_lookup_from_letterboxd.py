import json
import os
import re
import requests
from dotenv import load_dotenv
from logger import get_logger

load_dotenv()
TMDB_API_KEY = os.getenv('TMDB_API_KEY', '')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(BASE_DIR, 'cache')
os.makedirs(CACHE_DIR, exist_ok=True)

LETTERBOXD_CACHE = os.path.join(CACHE_DIR, 'letterboxd_watchlist_cache.json')
TMDB_CACHE = os.path.join(CACHE_DIR, 'tmdb_watchlist_cache.json')

def get_tmdb_id_from_api(title, year=None, api_key=None):
    logger = get_logger()
    if not api_key:
        logger.warning("No API key provided. Skipping TMDB lookup.")
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
        logger.debug(f"Searching for '{title}'" + (f" ({year})" if year and str(year).strip() else ""))
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        results = response.json().get('results', [])
        if results:
            logger.debug(f"Found TMDB ID {results[0]['id']} for '{title}'")
            return str(results[0]['id'])
        else:
            logger.debug(f"No results for '{title}'")
    except Exception as e:
        logger.error(f"API error for '{title}': {e}")
    return None

def tmdb_lookup_all(letterboxd_cache=LETTERBOXD_CACHE, tmdb_cache=TMDB_CACHE, api_key=None):
    logger = get_logger()
    if not api_key:
        load_dotenv()
        api_key = os.getenv('TMDB_API_KEY', '')
    if not os.path.exists(letterboxd_cache):
        logger.error(f"Cache file '{letterboxd_cache}' not found.")
        return []
    with open(letterboxd_cache, 'r') as f:
        films = json.load(f)
    logger.info(f"Loaded {len(films)} films from {letterboxd_cache}")
    tmdb_results = []
    for film in films:
        title = film.get('film_name')
        year = film.get('year')
        if not title or not title.strip():
            logger.warning(f"Skipping: missing title for film: {film}")
            continue
        tmdb_id = get_tmdb_id_from_api(title, year, api_key=api_key)
        tmdb_results.append({
            'film_name': title,
            'year': year,
            'tmdb_id': tmdb_id
        })
    with open(tmdb_cache, 'w') as f:
        json.dump(tmdb_results, f, indent=2)
    logger.info(f"Saved TMDB results for {len(tmdb_results)} films to {tmdb_cache}")
    return tmdb_results

if __name__ == "__main__":
    tmdb_lookup_all() 