import os
import logging
from dotenv import load_dotenv
import sys
from logger import setup_logging, get_logger, cleanup_old_logs

# Set up absolute paths for cache files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(BASE_DIR, 'cache')
LETTERBOXD_CACHE = os.path.join(CACHE_DIR, 'letterboxd_watchlist_cache.json')
TMDB_CACHE = os.path.join(CACHE_DIR, 'tmdb_watchlist_cache.json')
PLEX_CACHE = os.path.join(CACHE_DIR, 'plex_watchlist_cache.json')

# Import all modules
from letterboxd_watchlist_scraper import scrape_letterboxd_watchlist
from tmdb_lookup_from_letterboxd import tmdb_lookup_all
from plex_watchlist import main as plex_watchlist_main
from overseerr_monitor import overseerr_monitor_add_from_plex_cache
# Add import for the new multi-list sync
from lists.letterboxd_lists_to_plex import main as letterboxd_lists_to_plex_main

def main():
    # Setup logging
    debug_mode = os.getenv('DEBUG', '0') == '1'
    logger = setup_logging(logging.DEBUG if debug_mode else logging.INFO)
    load_dotenv()
    
    logger.info("=== Letterboxd Sync Script ===")
    
    # ============================================================================
    # SECTION 1: SCRAPE LETTERBOXD WATCHLIST
    # ============================================================================
    # Uncomment the next line to run the Letterboxd scraper
    RUN_SCRAPER = True
    
    if 'RUN_SCRAPER' in locals():
        logger.info("--- Step 1: Scraping Letterboxd Watchlist ---")
        letterboxd_username = os.getenv('LETTERBOXD_USERNAME')
        if not letterboxd_username:
            logger.error("LETTERBOXD_USERNAME environment variable is required")
            sys.exit(1)
        
        list_url = f"https://letterboxd.com/{letterboxd_username}/watchlist/"
        logger.info(f"Scraping Letterboxd watchlist for user: {letterboxd_username}")
        
        films = scrape_letterboxd_watchlist(list_url)
        if not films:
            logger.error("No films found in watchlist or error occurred during scraping")
            logger.error("Other functions cannot proceed without successful scraping")
            sys.exit(1)
        
        logger.info(f"Found {len(films)} films in watchlist")
        logger.info("Letterboxd scraping completed successfully!")
        logger.info("Proceeding to next step...")
        cleanup_old_logs()
    else:
        logger.info("Skipping Letterboxd scraper (RUN_SCRAPER not enabled)")
        logger.warning("Other functions may fail without fresh Letterboxd data")
    
    # ============================================================================
    # SECTION 2: TMDB LOOKUP
    # ============================================================================
    # Uncomment the next line to run TMDB lookup to get the IDs for each film
    RUN_TMDB_LOOKUP = True
    
    if 'RUN_TMDB_LOOKUP' in locals():
        logger.info("--- Step 2: TMDB Lookup ---")
        
        # Check if Letterboxd cache exists
        if not os.path.exists(LETTERBOXD_CACHE):
            logger.error(f"Letterboxd cache file '{LETTERBOXD_CACHE}' not found")
            logger.error("Please run the scraper first (enable RUN_SCRAPER)")
            sys.exit(1)
        
        tmdb_results = tmdb_lookup_all(letterboxd_cache=LETTERBOXD_CACHE, tmdb_cache=TMDB_CACHE)
        if not tmdb_results:
            logger.error("No TMDB results found")
            sys.exit(1)
        
        found_count = sum(1 for f in tmdb_results if f['tmdb_id'])
        logger.info(f"Found TMDB IDs for {found_count} out of {len(tmdb_results)} films")
        logger.info("TMDB lookup completed successfully!")
        cleanup_old_logs()
    else:
        logger.info("Skipping TMDB lookup (RUN_TMDB_LOOKUP not enabled)")
    
    # ============================================================================
    # SECTION 3: PLEX WATCHLIST PLAYLIST CREATION
    # ============================================================================
    # Uncomment the next line to create/update Plex playlist
    RUN_PLEX_PLAYLIST = True
    
    if 'RUN_PLEX_PLAYLIST' in locals():
        logger.info("--- Step 3: Plex Playlist Creation ---")
        
        # Check if TMDB cache exists
        if not os.path.exists(TMDB_CACHE):
            logger.error(f"TMDB cache file '{TMDB_CACHE}' not found")
            logger.error("Please run TMDB lookup first (enable RUN_TMDB_LOOKUP)")
            sys.exit(1)
        
        plex_host = os.getenv('PLEX_HOST')
        plex_token = os.getenv('PLEX_TOKEN')
        
        if not plex_host or not plex_token:
            logger.error("PLEX_HOST and PLEX_TOKEN environment variables are required")
            sys.exit(1)
        
        try:
            plex_watchlist_main()
            logger.info("Plex playlist creation completed successfully!")
            cleanup_old_logs()
        except Exception as e:
            logger.error(f"Error creating Plex playlist: {e}")
            sys.exit(1)
    else:
        logger.info("Skipping Plex watchlist creation (RUN_PLEX_PLAYLIST not enabled)")
    
    # ============================================================================
    # SECTION 4: OVERSEERR REQUESTS
    # ============================================================================
    # Uncomment the next line to request missing movies in Overseerr
    RUN_OVERSEERR_REQUESTS = True
    
    if 'RUN_OVERSEERR_REQUESTS' in locals():
        logger.info("--- Step 4: Overseerr Requests ---")
        
        # Check if Plex cache exists
        if not os.path.exists(PLEX_CACHE):
            logger.error(f"Plex cache file '{PLEX_CACHE}' not found")
            logger.error("Please run Plex playlist creation first (enable RUN_PLEX_PLAYLIST)")
            sys.exit(1)
        
        overseerr_host = os.getenv('OVERSEERR_HOST')
        overseerr_api_key = os.getenv('OVERSEERR_API_KEY')  # Using OVERSEERR_API_KEY from your .env
        
        if not overseerr_host or not overseerr_api_key:
            logger.error("OVERSEERR_HOST and OVERSEERR_API_KEY environment variables are required")
            sys.exit(1)
        
        try:
            overseerr_monitor_add_from_plex_cache()
            logger.info("Overseerr requests completed successfully!")
            cleanup_old_logs()
        except Exception as e:
            logger.error(f"Error processing Overseerr requests: {e}")
            sys.exit(1)
    else:
        logger.info("Skipping Overseerr requests (RUN_OVERSEERR_REQUESTS not enabled)")
    
    # ============================================================================
    # SECTION 5: LETTERBOXD MULTI-LIST TO PLEX SYNC
    # ============================================================================
    RUN_LETTERBOXD_LISTS_TO_PLEX = True

    if 'RUN_LETTERBOXD_LISTS_TO_PLEX' in locals():
        logger.info("--- Step 5: Letterboxd Multi-List to Plex Sync ---")
        try:
            letterboxd_lists_to_plex_main()
            logger.info("Letterboxd multi-list to Plex sync completed successfully!")
            cleanup_old_logs()
        except Exception as e:
            logger.error(f"Error in Letterboxd multi-list to Plex sync: {e}")
            sys.exit(1)
    else:
        logger.info("Skipping Letterboxd multi-list to Plex sync (RUN_LETTERBOXD_LISTS_TO_PLEX not enabled)")
    
    # ============================================================================
    # COMPLETION
    # ============================================================================
    logger.info("=== Script completed! ===")

if __name__ == "__main__":
    main()
