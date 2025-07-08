from bs4 import BeautifulSoup
import requests
import re
import time
import json
import os
from tqdm import tqdm
from dotenv import load_dotenv

CACHE_FILE = 'film_cache.json'
TMDB_API_KEY = os.getenv('TMDB_API_KEY', '')  # Optional TMDB API key for better lookups

def load_cache():
    """Load cached film data"""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            try:
                return json.load(f)
            except Exception:
                return {}
    return {}

def save_cache(cache):
    """Save film data to cache"""
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=2)

def get_tmdb_id_from_api(title, year=None):
    """Get TMDB ID using TMDB API search"""
    if not TMDB_API_KEY:
        return None
    
    try:
        # Clean title for search
        search_title = re.sub(r'[^\w\s]', '', title).strip()
        
        # Build search URL
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
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        results = response.json().get('results', [])
        if results:
            # Return the first (most relevant) result
            return str(results[0]['id'])
        
    except Exception as e:
        print(f"TMDB API error for '{title}': {e}")
    
    return None

def get_tmdb_id_from_film_page(film_slug):
    """Get TMDB ID by visiting the individual film page (fallback method)"""
    try:
        film_url = f"https://letterboxd.com/film/{film_slug}/"
        response = requests.get(film_url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for TMDB links
        tmdb_links = soup.find_all("a", href=re.compile(r"https://www.themoviedb.org/movie/"))
        for link in tmdb_links:
            href = link.get('href')
            if href:
                tmdb_match = re.search(r'^https:\/\/www\.themoviedb\.org\/movie\/([0-9]+)\/', href)
                if tmdb_match:
                    return tmdb_match.group(1)
        
    except Exception as e:
        print(f"Error getting TMDB ID from film page for {film_slug}: {e}")
    
    return None

def extract_films_from_page(soup):
    """Extract all film data from a watchlist page"""
    films = []
    
    # Find all film posters
    poster_list = soup.find('ul', class_='poster-list')
    if not poster_list:
        return films
    
    film_containers = poster_list.find_all('li', class_='poster-container')
    
    for container in film_containers:
        try:
            # Get the poster div with all the data attributes
            poster_div = container.find('div', class_='film-poster')
            if not poster_div:
                continue
            
            # Extract film data from data attributes
            film_data = {
                'film_id': poster_div.get('data-film-id'),
                'film_name': poster_div.get('data-film-name'),
                'film_slug': poster_div.get('data-film-slug'),
                'film_link': poster_div.get('data-film-link'),
                'poster_url': poster_div.get('data-poster-url')
            }
            
            # If film_name is still null, try to get it from the frame title
            if not film_data['film_name']:
                frame_title = poster_div.find('span', class_='frame-title')
                if frame_title:
                    title_text = frame_title.get_text()
                    # Remove year from title if present
                    title_without_year = re.sub(r'\s*\(\d{4}\)\s*$', '', title_text).strip()
                    film_data['film_name'] = title_without_year
            
            # Extract year from the frame title
            frame_title = poster_div.find('span', class_='frame-title')
            if frame_title:
                title_text = frame_title.get_text()
                year_match = re.search(r'\((\d{4})\)', title_text)
                if year_match:
                    film_data['year'] = year_match.group(1)
            
            # Try to get TMDB ID from API first
            if film_data['film_name'] and film_data.get('year'):
                tmdb_id = get_tmdb_id_from_api(film_data['film_name'], film_data['year'])
                if tmdb_id:
                    film_data['tmdb_id'] = tmdb_id
            
            # If no TMDB ID from API, try film page (but only if we have a slug)
            if not film_data.get('tmdb_id') and film_data.get('film_slug'):
                tmdb_id = get_tmdb_id_from_film_page(film_data['film_slug'])
                if tmdb_id:
                    film_data['tmdb_id'] = tmdb_id
            
            films.append(film_data)
            
        except Exception as e:
            print(f"Error extracting film data: {e}")
            continue
    
    return films

def get_total_film_count(soup):
    """Extract total film count from the page header"""
    try:
        count_element = soup.find('span', class_='js-watchlist-count')
        if count_element:
            count_text = count_element.get_text()
            # Extract number from "211 films" format
            match = re.search(r'(\d+)', count_text)
            if match:
                return int(match.group(1))
    except Exception as e:
        print(f"Error extracting film count: {e}")
    
    return None

def scrape_list(list_url):
    """Scrape watchlist with improved efficiency"""
    print(f"Scraping {list_url}")
    
    load_dotenv()  # Ensure .env is loaded before reading TMDB_API_KEY
    global TMDB_API_KEY
    TMDB_API_KEY = os.getenv('TMDB_API_KEY', '')
    
    cache = load_cache()
    all_films = []
    updated = False
    
    try:
        # Get the first page to determine total count and films per page
        response = requests.get(list_url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Get total film count
        total_films = get_total_film_count(soup)
        if total_films:
            print(f"Total films in watchlist: {total_films}")
        
        # Extract films from first page
        films = extract_films_from_page(soup)
        all_films.extend(films)
        
        # Calculate total pages (assuming 100 films per page based on HTML comment)
        films_per_page = 100
        total_pages = (total_films + films_per_page - 1) // films_per_page if total_films else 1
        
        print(f"Films per page: {films_per_page}, Total pages: {total_pages}")
        
        # If less than 5 pages, no need for rate limiting
        use_rate_limiting = total_pages >= 5
        
        # Process remaining pages
        for page in range(2, total_pages + 1):
            page_url = f"{list_url.rstrip('/')}/page/{page}/"
            print(f"Scraping page {page}/{total_pages}: {page_url}")
            
            if use_rate_limiting:
                time.sleep(2)  # Rate limiting for large watchlists
            
            try:
                response = requests.get(page_url, timeout=30)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                
                films = extract_films_from_page(soup)
                all_films.extend(films)
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    print(f"Rate limited. Waiting 60 seconds...")
                    time.sleep(60)
                    continue
                else:
                    print(f"Error fetching page {page}: {e}")
                    break
            except Exception as e:
                print(f"Error processing page {page}: {e}")
                break
        
        # Update cache with new film data
        for film in all_films:
            film_key = film.get('film_slug') or film.get('film_name')
            if film_key and film_key not in cache:
                cache[film_key] = film
                updated = True
        
        if updated:
            save_cache(cache)
        
        # Extract TMDB IDs for return
        tmdb_ids = []
        for film in all_films:
            if film.get('tmdb_id'):
                tmdb_ids.append(film['tmdb_id'])
        
        print(f"Successfully scraped {len(all_films)} films, found {len(tmdb_ids)} TMDB IDs")
        return tmdb_ids
        
    except requests.RequestException as e:
        print(f"Error fetching data from Letterboxd: {e}")
        if updated:
            save_cache(cache)
        return None
    except Exception as e:
        print(f"Unexpected error during scraping: {e}")
        if updated:
            save_cache(cache)
        return None