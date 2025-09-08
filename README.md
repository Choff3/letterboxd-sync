# letterboxd-sync

This a set of Python scripts that scrapes a [Letterboxd](https://letterboxd.com) watchlist and then adds the movies from that list to your [Plex](https://www.plex.tv/) watchlist. If a movie is not available in your Plex library, the missing movies will then be added to your [Radarr](https://github.com/Radarr/Radarr) instance. 

If the `PLEX_TOKEN` or `PLEX_HOST` variables are not applied, all movies on the watchlist will attempt to be added to Radarr. The script can also be used without Radarr.

## Getting API Tokens
### Plex
https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/

### Radarr
Your API key can be found in Settings > General in the Radarr Web UI.

### User Agent
A user agent must be provided to get around Letterboxd's bot protection. https://www.whatismybrowser.com/detect/what-is-my-user-agent/

## Sample run command
```
docker run --rm \
    -e LETTERBOXD_USERNAME='{Letterboxd username}' \
    -e PLEX_TOKEN='{Plex token}' \
    -e PLEX_HOST='http://{Plex server's IP}:32400' \
    -e RADARR_TOKEN='{radarr api key}' \
    -e RADARR_HOST='http://{Radarr instance IP}:7878' \
    -e USER_AGENT='{user agent}' \
    choff3/letterboxd-sync
```

## Acknowledgments

Thanks to L-Dot for the Letterboxd list scraper. https://github.com/L-Dot/Letterboxd-list-scraper
