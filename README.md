# letterboxd-sync

This is a set of Python scripts that scrapes a [Letterboxd](https://letterboxd.com) watchlist and then adds the movies from that list to your [Plex](https://www.plex.tv/) watchlist. If a movie is not available in your Plex library, the missing movies will then be added to your [Radarr](https://github.com/Radarr/Radarr) instance.

If the `PLEX_TOKEN` or `PLEX_HOST` variables are not applied, all movies on the watchlist will attempt to be added to Radarr. The script can also be used without Radarr.

## How It Works

1. **Scraping**: The script scrapes your Letterboxd watchlist to get movie information using minimal calls to avoid strict rate limiting
2. **ID Retrieval**: Searches TMDB for the ID of each movie for use with other APIs
3. **Plex Check**: For each movie, it checks if it's available in your Plex library
4. **Plex Watchlist**: Available movies are added to a Letterboxd Watchlist playlist in your Plex Library
5. **Shuffling:** Each time the script runs, the order of the playlist is changed to keep things fresh
6. **Radarr**: Movies not found in Plex are added to Radarr for monitoring
7. **Cleanup**: Movies no longer in your Letterboxd watchlist are removed from Plex watchlist

## Quick Setup

### Option 1: Automated Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-username/letterboxd-sync.git
cd letterboxd-sync

# Run the setup script
python3 setup.py
```

### Option 2: Manual Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp env.example .env

# Edit .env file with your configuration
nano .env
```

## Usage

### Local Development

```bash
python3 main.py
```

### Docker

```bash
docker run --rm \
    -e LETTERBOXD_USERNAME='your_letterboxd_username' \
    -e PLEX_TOKEN='your_plex_token' \
    -e PLEX_HOST='http://your_plex_server_ip:32400' \
    -e RADARR_TOKEN='your_radarr_api_key' \
    -e RADARR_HOST='http://your_radarr_instance_ip:7878' \
    choff3/letterboxd-sync
```

### Scheduled Execution

You can set up a cron job to run this script periodically:

```bash
# Add to crontab (runs every 6 hours)
0 */6 * * * cd /path/to/letterboxd-sync && python3 main.py
```

## Troubleshooting

### Debug Mode

Set the `DEBUG` environment variable to see more detailed output:

```bash
export DEBUG=1
python3 main.py
```

## Acknowledgments

Thanks to Teddy for providing all these services and writing the first version of this. https://github.com/L-Dot/Letterboxd-list-scraper

## License

This project is licensed under the MIT License - see the LICENSE file for details.
