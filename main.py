from list_scraper import scrape_list
#import from plex_watchlist import plex_watchlist_add
#import from radarr_monitor import radarr_monitor_add
import os
import logging
from dotenv import load_dotenv
import sys
from logger import setup_logging, get_logger
#from tmdb_lookup_from_letterboxd import tmdb_lookup_all
#import json

def main():
    # Setup logging
    debug_mode = os.getenv('DEBUG', '0') == '1'
    logger = setup_logging(logging.DEBUG if debug_mode else logging.INFO)
    load_dotenv()

    # Scrape Letterboxd and write to letterboxd_cache.json
    letterboxd_username = os.getenv('LETTERBOXD_USERNAME')
    if not letterboxd_username:
        logger.error("LETTERBOXD_USERNAME environment variable is required")
        logger.error("Please set it in your .env file or as an environment variable")
        sys.exit(1)
    list_url = f"https://letterboxd.com/{letterboxd_username}/watchlist/"
    logger.info(f"Scraping Letterboxd watchlist for user: {letterboxd_username}")
    films = scrape_list(list_url)
    if not films:
        logger.error("No films found in watchlist or error occurred during scraping")
        sys.exit(1)
    logger.info(f"Found {len(films)} films in watchlist (first page or all, depending on config)")

    # --- The following steps are commented out for testing only the scraper ---
    # logger.info("Running TMDB lookup for scraped films...")
    # tmdb_results = tmdb_lookup_all()
    # if not tmdb_results:
    #     logger.error("No TMDB results found. Exiting.")
    #     sys.exit(1)
    # logger.info(f"Found TMDB IDs for {sum(1 for f in tmdb_results if f['tmdb_id'])} films.")

    # plex_token = os.getenv('PLEX_TOKEN')
    # plex_host = os.getenv('PLEX_HOST')
    # tmdb_ids = [f['tmdb_id'] for f in tmdb_results if f['tmdb_id']]
    # if plex_token and plex_host and tmdb_ids:
    #     logger.info("Adding films to Plex watchlist...")
    #     radarr_films = plex_watchlist_add(tmdb_ids, plex_host, plex_token)
    #     logger.info(f"Added {len(tmdb_ids) - len(radarr_films)} films to Plex watchlist")
    #     logger.info(f"{len(radarr_films)} films not found in Plex library")
    # else:
    #     logger.info("Skipping Plex (PLEX_TOKEN or PLEX_HOST not configured, or no TMDB IDs)")
    #     radarr_films = tmdb_ids

    # radarr_host = os.getenv('RADARR_HOST')
    # radarr_api = os.getenv('RADARR_TOKEN')
    # if radarr_api and radarr_host and radarr_films:
    #     logger.info("Adding films to Radarr...")
    #     radarr_monitor_add(radarr_films, radarr_host, radarr_api)
    # else:
    #     logger.info("Skipping Radarr (RADARR_TOKEN, RADARR_HOST not configured, or no films to add)")

    # logger.info("Sync completed successfully!")

if __name__ == "__main__":
    main()
