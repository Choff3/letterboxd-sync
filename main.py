from list_scraper import *
from plex_watchlist import *
from radarr_monitor import *
import os
import logging
from dotenv import load_dotenv
import sys
from logger import setup_logging, get_logger

def main():
    # Setup logging
    debug_mode = os.getenv('DEBUG', '0') == '1'
    logger = setup_logging(logging.DEBUG if debug_mode else logging.INFO)
    
    # Load environment variables from .env file
    load_dotenv()

    # Scrape letterboxd watchlist
    letterboxd_username = os.getenv('LETTERBOXD_USERNAME')
    if not letterboxd_username:
        logger.error("LETTERBOXD_USERNAME environment variable is required")
        logger.error("Please set it in your .env file or as an environment variable")
        sys.exit(1)
    
    list_url = "https://letterboxd.com/"+letterboxd_username+"/watchlist/"
    logger.info(f"Scraping Letterboxd watchlist for user: {letterboxd_username}")
    films = scrape_list(list_url)
    
    if not films:
        logger.error("No films found in watchlist or error occurred during scraping")
        sys.exit(1)
    
    logger.info(f"Found {len(films)} films in watchlist")

    # Add films to Plex watchlist
    plex_token = os.getenv('PLEX_TOKEN')
    plex_host = os.getenv('PLEX_HOST')
    if plex_token and plex_host:
        logger.info("Adding films to Plex watchlist...")
        radarr_films = plex_watchlist_add(films, plex_host, plex_token)
        logger.info(f"Added {len(films) - len(radarr_films)} films to Plex watchlist")
        logger.info(f"{len(radarr_films)} films not found in Plex library")
    else:
        logger.info("Skipping Plex (PLEX_TOKEN or PLEX_HOST not configured)")
        radarr_films = films

    # Add films to Radarr
    radarr_host = os.getenv('RADARR_HOST')
    radarr_api = os.getenv('RADARR_TOKEN')
    if radarr_api and radarr_host and radarr_films:
        logger.info("Adding films to Radarr...")
        radarr_monitor_add(radarr_films, radarr_host, radarr_api)
    else:
        logger.info("Skipping Radarr (RADARR_TOKEN, RADARR_HOST not configured, or no films to add)")

    logger.info("Sync completed successfully!")

if __name__ == "__main__":
    main()
