import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from plexapi.server import PlexServer
from dotenv import load_dotenv
import logging

# Setup paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LISTS_DIR = BASE_DIR  # The lists/ directory is the same as this script's directory
os.makedirs(LISTS_DIR, exist_ok=True)

LIST_SLUGS_FILE = os.path.join(BASE_DIR, 'letterboxd_lists.txt')
LISTS_CACHE_FILE = os.path.join(os.path.dirname(BASE_DIR), 'cache', 'letterboxd_lists_cache.json')
PLEX_LIST_CACHE_FILE = os.path.join(os.path.dirname(BASE_DIR), 'cache', 'plex_list_cache.json')

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

RATE_LIMIT_LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs', 'letterboxd-rate-limit')
def log_rate_limit_event(message):
    with open(RATE_LIMIT_LOG, 'a') as f:
        f.write(f"{datetime.now().strftime('%I:%M%p %B %d, %Y')} {message}\n")

def test_scrape_lists_page_to_json():
    """Scrape all pages of the user's Letterboxd lists, extract list names and links, and save as JSON in list_names.json. Uses robust rate limiting and retry logic."""
    if not LETTERBOXD_USERNAME:
        print("[ERROR] LETTERBOXD_USERNAME not set in .env.")
        return
    base_url = f"https://letterboxd.com/{LETTERBOXD_USERNAME}/lists/"
    print(f"[INFO] Scraping lists page: {base_url}")
    list_objs = []
    page = 1
    while True:
        if page == 1:
            page_url = base_url
        else:
            page_url = f"{base_url}page/{page}/"
        print(f"[INFO] Fetching page {page}: {page_url}")
        for attempt in range(MAX_RETRIES):
            try:
                response = requests.get(page_url, timeout=30)
                if response.status_code == 429:
                    log_rate_limit_event(f"Hit rate limit on attempt {attempt + 1}. Waiting {RETRY_DELAY} seconds...")
                    import time; time.sleep(RETRY_DELAY)
                    continue
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                for section in soup.find_all('section', class_='list'):
                    h2 = section.find('h2', class_='title-2')
                    if h2:
                        a = h2.find('a', href=True)
                        if a:
                            name = a.get_text(strip=True)
                            url = a['href']
                            # Make absolute URL
                            if url.startswith('/'):
                                url = f"https://letterboxd.com{url}"
                            list_objs.append({'name': name, 'url': url})
                # Check for next page
                pagination = soup.find('div', class_='pagination')
                next_link = pagination.find('a', class_='next') if pagination else None
                if not next_link:
                    break
                page += 1
                import time; time.sleep(RATE_LIMIT_DELAY)
                break  # break retry loop if successful
            except requests.exceptions.RequestException as e:
                print(f"[ERROR] Request failed on attempt {attempt + 1}: {e}")
                if attempt < MAX_RETRIES - 1:
                    print(f"[RETRY] Waiting {RATE_LIMIT_DELAY} seconds before retry...")
                    import time; time.sleep(RATE_LIMIT_DELAY)
                else:
                    print(f"[FATAL] All {MAX_RETRIES} attempts failed for page {page}")
                    break
        else:
            # If we exhausted all retries, stop scraping
            break
        # If we broke out of the retry loop due to no next page, stop
        if not (pagination and next_link):
            break
    output_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'cache', 'list_names.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(list_objs, f, indent=2)
    print(f"[INFO] Saved list names and URLs to {output_file}")

# (Other functions from the previous script would go here if needed) 