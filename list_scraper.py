from bs4 import BeautifulSoup
import requests
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

        print(films)
        
        for film in tqdm(films):
            
            panel = film.find('div').find('img')
            title = panel['alt']

            film_card = film.find('div').get('data-target-link')
            film_page = 'https://letterboxd.com/' + film_card
            filmget = requests.get(film_page)
            film_soup = BeautifulSoup(filmget.content, 'html.parser')

            director = film_soup.find('meta', attrs={'name':'twitter:data1'}).attrs['content']

            parsed_film = (title,director)
            watchlist.append(parsed_film)

        next = soup.find('a', class_='next')
        if next is None:
            break
        else:
            list_link = 'https://letterboxd.com/' + next['href']
            
    return watchlist