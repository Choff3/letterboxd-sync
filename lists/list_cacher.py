import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from plexapi.server import PlexServer
from dotenv import load_dotenv

# Setup paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LISTS_DIR = BASE_DIR  # The lists/ directory is the same as this script's directory
os.makedirs(LISTS_DIR, exist_ok=True)

LIST_SLUGS_FILE = os.path.join(BASE_DIR, 'letterboxd_lists.txt')
LISTS_CACHE_FILE = os.path.join(LISTS_DIR, 'letterboxd_lists_cache.json')
PLEX_LIST_CACHE_FILE = os.path.join(LISTS_DIR, 'plex_list_cache.json')

# Load environment variables
load_dotenv()

# Plex config
PLEX_HOST = os.getenv('PLEX_HOST')
PLEX_TOKEN = os.getenv('PLEX_TOKEN')
LETTERBOXD_USERNAME = os.getenv('LETTERBOXD_USERNAME')
TMDB_API_KEY = os.getenv('TMDB_API_KEY', '')

RATE_LIMIT_DELAY = 2
MAX_RETRIES = 3
RETRY_DELAY = 30


def fetch_letterboxd_list_with_pagination(slug):
    """Scrape a Letterboxd list by slug, handling pagination and rate limiting. Returns its title and all movies."""
    if not LETTERBOXD_USERNAME:
        print("[ERROR] LETTERBOXD_USERNAME not set in .env.")
        return {'title': slug, 'movies': []}
    url = f"https://letterboxd.com/{LETTERBOXD_USERNAME}/list/{slug}/"
    print(f"[INFO] Scraping list: {url}")
    all_movies = []
    page = 1
    title = slug
    while True:
        if page == 1:
            page_url = url
        else:
            page_url = f"{url}page/{page}/"
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
                        film_data = {
                            'letterboxd_film_id': poster_div.get('data-film-id'),
                            'film_slug': film_slug,
                            'film_link': poster_div.get('data-film-link'),
                            'poster_url': poster_div.get('data-poster-url'),
                            'film_name': film_name,
                            'year': year,
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


def list_cacher():
    # Read list slugs
    if not os.path.exists(LIST_SLUGS_FILE):
        print(f"[ERROR] {LIST_SLUGS_FILE} not found.")
        return
    with open(LIST_SLUGS_FILE, 'r') as f:
        slugs = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    print(f"[INFO] Found {len(slugs)} list slugs.")

    # Scrape each list and build cache
    lists_cache = {}
    for slug in slugs:
        lists_cache[slug] = fetch_letterboxd_list_with_pagination(slug)
    with open(LISTS_CACHE_FILE, 'w') as f:
        json.dump(lists_cache, f, indent=2)
    print(f"[INFO] Saved all lists to {LISTS_CACHE_FILE}")

    # Plex integration
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
            name = film.get('film_name')
            year = film.get('year')
            print(f"[DEBUG] Processing film: {name} (Year: {year}) for list {playlist_name}")
            try:
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
                        'date_added': date_added,
                        'availability': 'Available in Library'
                    })
                else:
                    print(f"[DEBUG] No results found for '{name}'.")
                    plex_results.append({
                        'film_name': name,
                        'date_added': '',
                        'availability': 'Not in Library'
                    })
            except Exception as e:
                print(f"[ERROR] Searching for '{name}': {e}")
                plex_results.append({
                    'film_name': name,
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


def test_scrape_lists_to_html():
    # Read list slugs
    if not os.path.exists(LIST_SLUGS_FILE):
        print(f"[ERROR] {LIST_SLUGS_FILE} not found.")
        return
    with open(LIST_SLUGS_FILE, 'r') as f:
        slugs = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    print(f"[INFO] Found {len(slugs)} list slugs.")

    html_results = []
    for slug in slugs:
        url = f"https://letterboxd.com/{slug}/"
        print(f"[INFO] Fetching HTML for: {url}")
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            html_results.append(f"<h2>{slug}</h2>\n" + response.text)
        except Exception as e:
            html_results.append(f"<h2>{slug}</h2>\n<p>Error: {e}</p>")
    # Save in the same directory as this script
    output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_list_results.html')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("<html><body>\n" + "\n<hr>\n".join(html_results) + "\n</body></html>")
    print(f"[INFO] Saved HTML results to {output_file}")

# TMDB lookup logic (copied from tmdb_lookup_from_letterboxd.py)
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

def fetch_letterboxd_list_with_pagination_and_tmdb(slug):
    """Scrape a Letterboxd list by slug, handle pagination, and add TMDB IDs. Only include film_name, year, tmdb_id, date_scraped in output."""
    if not LETTERBOXD_USERNAME:
        print("[ERROR] LETTERBOXD_USERNAME not set in .env.")
        return {'title': slug, 'movies': []}
    url = f"https://letterboxd.com/{LETTERBOXD_USERNAME}/list/{slug}/"
    print(f"[INFO] Scraping list: {url}")
    all_movies = []
    page = 1
    title = slug
    while True:
        if page == 1:
            page_url = url
        else:
            page_url = f"{url}page/{page}/"
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

def scrape_lists_to_json_cache():
    # Read list slugs
    if not os.path.exists(LIST_SLUGS_FILE):
        print(f"[ERROR] {LIST_SLUGS_FILE} not found.")
        return
    with open(LIST_SLUGS_FILE, 'r') as f:
        slugs = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    print(f"[INFO] Found {len(slugs)} list slugs.")

    # Warn if any slug contains a slash (user error)
    for slug in slugs:
        if '/' in slug:
            print(f"[WARNING] Slug '{slug}' contains a slash. Only the list slug (e.g. 'should-rewatch') should be used.")

    # Scrape each list and build cache
    lists_cache = {}
    for slug in slugs:
        lists_cache[slug] = fetch_letterboxd_list_with_pagination_and_tmdb(slug)
    with open(LISTS_CACHE_FILE, 'w') as f:
        json.dump(lists_cache, f, indent=2)
    print(f"[INFO] Saved all lists to {LISTS_CACHE_FILE}")

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

# Update main block to run Plex playlist creation after scraping
if __name__ == '__main__':
    scrape_lists_to_json_cache()
    # Load the just-saved cache
    with open(LISTS_CACHE_FILE, 'r') as f:
        lists_cache = json.load(f)
    plex_playlists_from_lists_cache(lists_cache) 