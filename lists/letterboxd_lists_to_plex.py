import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from plexapi.server import PlexServer
from dotenv import load_dotenv

# Setup paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LISTS_DIR = BASE_DIR
os.makedirs(LISTS_DIR, exist_ok=True)

LIST_NAMES_FILE = os.path.join(LISTS_DIR, 'list_names.json')
LISTS_CACHE_FILE = os.path.join(LISTS_DIR, 'letterboxd_lists_cache.json')
PLEX_LIST_CACHE_FILE = os.path.join(LISTS_DIR, 'plex_list_cache.json')

# Load environment variables
load_dotenv()

PLEX_HOST = os.getenv('PLEX_HOST')
PLEX_TOKEN = os.getenv('PLEX_TOKEN')
LETTERBOXD_USERNAME = os.getenv('LETTERBOXD_USERNAME')
TMDB_API_KEY = os.getenv('TMDB_API_KEY', '')

RATE_LIMIT_DELAY = 2
MAX_RETRIES = 3
RETRY_DELAY = 30

# TMDB lookup logic
def get_tmdb_id_from_api(title, year=None, api_key=None):
    if not api_key:
        print("[TMDB] No API key provided. Skipping TMDB lookup.")
        return None
    try:
        import re
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

def fetch_letterboxd_list_with_pagination_and_tmdb(list_url, list_name):
    """Scrape a Letterboxd list by URL, handle pagination, and add TMDB IDs. Only include film_name, year, tmdb_id, date_scraped in output."""
    print(f"[INFO] Scraping list: {list_url}")
    all_movies = []
    page = 1
    title = list_name
    while True:
        if page == 1:
            page_url = list_url
        else:
            page_url = f"{list_url}page/{page}/"
        for attempt in range(MAX_RETRIES):
            try:
                response = requests.get(page_url, timeout=30)
                if response.status_code == 429:
                    print(f"[RATE LIMIT] Hit rate limit. Waiting {RETRY_DELAY} seconds...")
                    import time; time.sleep(RETRY_DELAY)
                    continue
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                # Get list title from first page only
                if page == 1:
                    title_tag = soup.find('h1', class_='headline-1')
                    if title_tag:
                        title = title_tag.get_text(strip=True)
                # Get all movies on the page
                poster_list = soup.find('ul', class_='poster-list')
                if not poster_list:
                    return {'title': title, 'movies': all_movies}
                film_containers = poster_list.find_all('li', class_='poster-container')
                for container in film_containers:
                    try:
                        poster_div = container.find('div', class_='film-poster')
                        if not poster_div:
                            continue
                        img = poster_div.find('img', class_='image')
                        film_name = img['alt'].strip() if img and img.has_attr('alt') else ''
                        film_slug = poster_div.get('data-film-slug', '')
                        year = ''
                        if len(film_slug) >= 4 and film_slug[-4:].isdigit():
                            year = film_slug[-4:]
                        tmdb_id = get_tmdb_id_from_api(film_name, year, api_key=TMDB_API_KEY)
                        film_data = {
                            'film_name': film_name,
                            'year': year,
                            'tmdb_id': tmdb_id,
                            'date_scraped': datetime.now().strftime('%b %d %Y %I:%M%p').lower()
                        }
                        all_movies.append(film_data)
                    except Exception as e:
                        print(f"Error extracting film data: {e}")
                        continue
                # Check for next page
                pagination = soup.find('div', class_='pagination')
                next_link = pagination.find('a', class_='next') if pagination else None
                if not next_link:
                    return {'title': title, 'movies': all_movies}
                page += 1
                import time; time.sleep(RATE_LIMIT_DELAY)
                break  # break retry loop if successful
            except Exception as e:
                print(f"[ERROR] Failed to scrape {page_url}: {e}")
                if attempt < MAX_RETRIES - 1:
                    import time; time.sleep(RATE_LIMIT_DELAY)
                else:
                    return {'title': title, 'movies': all_movies}
    return {'title': title, 'movies': all_movies}

def plex_playlists_from_lists_cache(lists_cache):
    if not PLEX_HOST or not PLEX_TOKEN:
        print("[ERROR] PLEX_HOST and PLEX_TOKEN must be set in .env for Plex integration.")
        return
    try:
        server = PlexServer(PLEX_HOST, PLEX_TOKEN)
        print(f"[DEBUG] Connected to Plex server: {server.friendlyName}")
        movies_section = server.library.section('Movies')
    except Exception as e:
        print(f"[ERROR] {e}")
        return
    plex_list_cache = {}
    for slug, list_data in lists_cache.items():
        playlist_name = list_data['title']
        movies = list_data['movies']
        items_to_add = []
        plex_results = []
        for film in movies:
            tmdb_id = film.get('tmdb_id')
            name = film.get('film_name')
            year = film.get('year')
            print(f"[DEBUG] Processing film: {name} (TMDB: {tmdb_id}, Year: {year}) for list {playlist_name}")
            try:
                # Search Plex by TMDB ID if possible, else by name/year
                results = []
                if tmdb_id:
                    results = movies_section.search(guid=f"tmdb://{tmdb_id}")
                if not results:
                    if year:
                        results = movies_section.search(title=name, year=year)
                    else:
                        results = movies_section.search(title=name)
                if results:
                    print(f"[DEBUG] Found {len(results)} result(s) for '{name}'. Adding to playlist.")
                    items_to_add.append(results[0])
                    date_added = datetime.now().strftime('%b %d %Y %I:%M%p').lower()
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
        # Create or update playlist
        playlist = None
        for pl in server.playlists():
            if pl.title == playlist_name:
                playlist = pl
                print(f"[DEBUG] Found existing playlist: {playlist_name}")
                break
        if items_to_add:
            if not playlist:
                print(f"[DEBUG] Creating new playlist: {playlist_name}")
                playlist = server.createPlaylist(playlist_name, items=items_to_add)
            else:
                try:
                    playlist.reload()
                    current_items = list(playlist.items())
                    items_to_remove = [item for item in current_items if item not in items_to_add]
                    if items_to_remove:
                        playlist.removeItems(items_to_remove)
                        print(f"[DEBUG] Removed {len(items_to_remove)} items from playlist '{playlist_name}'.")
                    playlist.addItems([item for item in items_to_add if item not in current_items])
                    print(f"[DEBUG] Updated playlist '{playlist_name}' with {len(items_to_add)} items.")
                except Exception as e:
                    print(f"[ERROR] Updating playlist '{playlist_name}': {e}")
        plex_list_cache[playlist_name] = plex_results
    with open(PLEX_LIST_CACHE_FILE, 'w') as f:
        json.dump(plex_list_cache, f, indent=2)
    print(f"[INFO] Saved Plex list cache to {PLEX_LIST_CACHE_FILE}")

def main():
    # Step 1: Run get_letterboxd_lists.py to get all lists and names
    from get_letterboxd_lists import test_scrape_lists_page_to_json
    test_scrape_lists_page_to_json()
    # Step 2: Load list_names.json
    with open(LIST_NAMES_FILE, 'r') as f:
        list_objs = json.load(f)
    print(f"[INFO] Loaded {len(list_objs)} lists from list_names.json")
    # Step 3: Scrape each list and build cache
    lists_cache = {}
    for obj in list_objs:
        name = obj['name']
        url = obj['url']
        # Remove trailing slash for slug extraction if needed
        slug = url.rstrip('/').split('/')[-1]
        lists_cache[slug] = fetch_letterboxd_list_with_pagination_and_tmdb(url, name)
    with open(LISTS_CACHE_FILE, 'w') as f:
        json.dump(lists_cache, f, indent=2)
    print(f"[INFO] Saved all lists to {LISTS_CACHE_FILE}")
    # Step 4: Create/update Plex playlists
    plex_playlists_from_lists_cache(lists_cache)

if __name__ == '__main__':
    main() 