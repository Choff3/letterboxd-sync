from bs4 import BeautifulSoup
import requests
import re
import time
import json
import os
from tqdm import tqdm
from dotenv import load_dotenv
import datetime

CACHE_FILE = 'cache/letterboxd_cache.json'
TMDB_API_KEY = os.getenv('TMDB_API_KEY', '')  # Optional TMDB API key for better lookups

def load_cache():
    """
    Load the film cache from the CACHE_FILE (film_cache.json).
    Returns a dictionary mapping film slugs or names to their cached data.
    """
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            try:
                return json.load(f)
            except Exception:
                return {}
    return {}

def save_cache(cache):
    """
    Save the given cache dictionary to the CACHE_FILE (film_cache.json).
    """
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=2)

def get_tmdb_id_from_api(title, year=None):
    """
    Query the TMDB API for a movie by title and (optionally) year.
    Returns the TMDB ID as a string if found, otherwise None.
    Logs the search and result to the console.
    """
    if not TMDB_API_KEY:
        print("[TMDB] No API key provided. Skipping TMDB lookup.")
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
        
        print(f"[TMDB] Searching for '{title}' ({year})...")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        results = response.json().get('results', [])
        if results:
            # Return the first (most relevant) result
            print(f"[TMDB] Found TMDB ID {results[0]['id']} for '{title}' ({year})")
            return str(results[0]['id'])
        else:
            print(f"[TMDB] No results for '{title}' ({year})")
        
    except Exception as e:
        print(f"[TMDB] API error for '{title}': {e}")
    
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
    """
    Extract all film data from a single Letterboxd watchlist page.
    For each film, extract the name from the alt property of the image with class='image',
    and the year from the end of the data-film-slug attribute (if last 4 chars are digits, else year is empty).
    Returns a list of film data dictionaries (no TMDB lookup).
    """
    films = []
    poster_list = soup.find('ul', class_='poster-list')
    if not poster_list:
        return films
    film_containers = poster_list.find_all('li', class_='poster-container')
    now = datetime.datetime.now().strftime('%b %d %Y %I:%M%p').lower().replace('am', 'am').replace('pm', 'pm')
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
                'film_id': poster_div.get('data-film-id'),
                'film_slug': film_slug,
                'film_link': poster_div.get('data-film-link'),
                'poster_url': poster_div.get('data-poster-url'),
                'film_name': film_name,
                'year': year,
                'date_scraped': now
            }
            films.append(film_data)
        except Exception as e:
            print(f"Error extracting film data: {e}")
            continue
    return films

def get_total_film_count(soup):
    """
    Extract the total number of films in the watchlist from the page header.
    Returns the count as an integer, or None if not found.
    """
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
    """
    Use requests to load the Letterboxd watchlist page, print the entire HTML, extract all films, and save to letterboxd_cache.json.
    """
    print(f"Scraping {list_url} with requests...")
    all_films = []
    try:
        import requests
        response = requests.get(list_url, timeout=30)
        print("\n--- BEGIN RAW HTML ---\n")
        print(response.text)
        print("\n--- END RAW HTML ---\n")
        soup = BeautifulSoup(response.text, 'html.parser')
        films = extract_films_from_page(soup)
        all_films.extend(films)
        with open(CACHE_FILE, 'w') as f:
            json.dump(all_films, f, indent=2)
        print(f"Saved {len(all_films)} films to {CACHE_FILE}")
        return all_films
    except Exception as e:
        print(f"Error fetching data from Letterboxd: {e}")
        return None