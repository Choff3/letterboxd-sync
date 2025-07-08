from bs4 import BeautifulSoup
import requests
import re
from tqdm import tqdm

def scrape_list(list_link):
    print("Scraping "+list_link)

    watchlist = []

    try:
        while True:
            list_page = requests.get(list_link, timeout=30)
            list_page.raise_for_status()
            
            soup = BeautifulSoup(list_page.content, 'html.parser')
            
            table = soup.find('ul', class_='poster-list')
            if table is None:
                print("No poster-list found on page. The page structure may have changed.")
                return None
            
            films = table.find_all('li')
            
            for film in tqdm(films, desc="Processing films"):
                try:
                    film_div = film.find('div')
                    if not film_div:
                        continue
                        
                    film_card = film_div.get('data-target-link')
                    if not film_card:
                        continue
                        
                    film_page = 'https://letterboxd.com/' + film_card
                    filmget = requests.get(film_page, timeout=30)
                    filmget.raise_for_status()
                    film_soup = BeautifulSoup(filmget.content, 'html.parser')

                    # Parse TMDB URLs to get the TMDB ID
                    tmdb_urls = film_soup.find_all("a", href=re.compile(r"https://www.themoviedb.org/movie/"))
                    for tmdb_url in tmdb_urls:
                        href = tmdb_url.get('href')
                        if href:
                            tmdb_id = re.search(r'^https:\/\/www\.themoviedb\.org\/movie\/([0-9]+)\/', href)
                            if tmdb_id and tmdb_id.group(1) not in watchlist:
                                watchlist.append(tmdb_id.group(1))
                                break
                except Exception as e:
                    print(f"Error processing film: {e}")
                    continue

            next_link = soup.find('a', class_='next')
            if next_link is None:
                break
            else:
                href = next_link.get('href')
                if href:
                    list_link = 'https://letterboxd.com/' + href
                
        return watchlist
        
    except requests.RequestException as e:
        print(f"Error fetching data from Letterboxd: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error during scraping: {e}")
        return None