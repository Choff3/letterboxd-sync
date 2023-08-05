from bs4 import BeautifulSoup
import requests
import re
from tqdm import tqdm

def scrape_list(list_link):

    watchlist = []

    while True:
        list_page = requests.get(list_link)
        
        if list_page.status_code != 200:
            encounter_error("")
        soup = BeautifulSoup(list_page.content, 'html.parser')
        
        table = soup.find('ul', class_='poster-list')
        if table is None:
            return None
        
        films = table.find_all('li')
        
        for film in tqdm(films):

            film_card = film.find('div').get('data-target-link')
            film_page = 'https://letterboxd.com/' + film_card
            filmget = requests.get(film_page)
            film_soup = BeautifulSoup(filmget.content, 'html.parser')

            # TODO: Parse the return of below to get the TMDB ID. Then use that to add movies to Plex watchlist and Radarr.
            tmdb_urls = film_soup.find_all("a", href=re.compile(r"https://www.themoviedb.org/movie/"))
            for tmdb_url in tmdb_urls:
                tmdb_id = re.search(r'^https:\/\/www\.themoviedb\.org\/movie\/([0-9]+)\/',tmdb_url['href'])
                watchlist.append(tmdb_id.group(1))

        next = soup.find('a', class_='next')
        if next is None:
            break
        else:
            list_link = 'https://letterboxd.com/' + next['href']
            
    print(watchlist)
    return watchlist