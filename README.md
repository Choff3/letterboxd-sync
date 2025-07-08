# letterboxd-sync

This is a set of Python scripts that scrapes a [Letterboxd](https://letterboxd.com) watchlist and then adds the movies from that list to your [Plex](https://www.plex.tv/) watchlist. If a movie is not available in your Plex library, the missing movies will then be added to your [Radarr](https://github.com/Radarr/Radarr) instance.

If the `PLEX_TOKEN` or `PLEX_HOST` variables are not applied, all movies on the watchlist will attempt to be added to Radarr. The script can also be used without Radarr.

## Features

- Scrapes your Letterboxd watchlist for movies
- Adds available movies to your Plex watchlist
- Adds missing movies to Radarr for monitoring and downloading
- Removes movies from Plex watchlist that are no longer in your Letterboxd watchlist
- Supports pagination for large watchlists
- Error handling and logging

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

## Configuration

### Required Environment Variables

- `LETTERBOXD_USERNAME`: Your Letterboxd username

### Optional Environment Variables

- `PLEX_TOKEN`: Your Plex authentication token
- `PLEX_HOST`: Your Plex server URL (e.g., `http://192.168.1.100:32400`)
- `RADARR_TOKEN`: Your Radarr API key
- `RADARR_HOST`: Your Radarr server URL (e.g., `http://192.168.1.100:7878`)

## Getting API Tokens

### Plex

1. Go to https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/
2. Follow the instructions to find your authentication token

### Radarr

1. Open your Radarr web interface
2. Go to Settings > General
3. Copy your API key

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

## How It Works

1. **Scraping**: The script scrapes your Letterboxd watchlist to get movie information
2. **Plex Check**: For each movie, it checks if it's available in your Plex library
3. **Plex Watchlist**: Available movies are added to your Plex watchlist
4. **Radarr**: Movies not found in Plex are added to Radarr for monitoring
5. **Cleanup**: Movies no longer in your Letterboxd watchlist are removed from Plex watchlist

## Troubleshooting

### Common Issues

1. **"No poster-list found on page"**: Letterboxd may have changed their page structure. Check if the script needs updating.

2. **"Error connecting to Plex"**: Verify your PLEX_TOKEN and PLEX_HOST are correct.

3. **"Error connecting to Radarr"**: Verify your RADARR_TOKEN and RADARR_HOST are correct.

4. **SSL Warnings**: These are warnings and don't affect functionality. You can suppress them by updating your Python installation.

### Debug Mode

Set the `DEBUG` environment variable to see more detailed output:

```bash
export DEBUG=1
python3 main.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Acknowledgments

Thanks to L-Dot for the Letterboxd list scraper. https://github.com/L-Dot/Letterboxd-list-scraper

## License

This project is licensed under the MIT License - see the LICENSE file for details.
