from list_scraper import *
from plex_watchlist import *
import os
from dotenv import load_dotenv

def main():

    load_dotenv()

    letterboxd_username = os.getenv('LETTERBOXD_USERNAME')
    
    list_url = "https://letterboxd.com/"+letterboxd_username+"/watchlist/"
            
    list_url.split('/')[-3]

    films = scrape_list(list_url)

    plex_watchlist_add(films)

if __name__ == "__main__":
    main()
