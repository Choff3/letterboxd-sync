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

## Scheduled Execution (Run Every 15 Minutes)

You can use cron to run the script automatically every 15 minutes:

1. **Open Terminal**
2. Edit your crontab:
   ```bash
   crontab -e
   ```
3. Add this line (replace `/path/to/letterboxd-sync` with your actual project path):
   ```
   */15 * * * * cd /path/to/letterboxd-sync && /usr/bin/env python3 main.py >> logs/cron.log 2>&1
   ```
4. **Save and exit:**
   - Press `Esc`, then type `:wq`, then press `Enter`
5. **Check your cron jobs:**
   ```bash
   crontab -l
   ```

This will run the script every 15 minutes and log output to `logs/cron.log`.

## Troubleshooting

### Debug Mode

Set the `
