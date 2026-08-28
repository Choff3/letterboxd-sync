# letterboxd-sync

Grabs a [Letterboxd](https://letterboxd.com) watchlist using [https://github.com/screeny05/letterboxd-list-radarr](https://github.com/screeny05/letterboxd-list-radarr) and then adds the movies from that list to your [Plex](https://www.plex.tv/) watchlist.

## Getting Plex Token
https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/

## Run with docker-compose
```
services:
    letterboxd-sync:
        image: ghcr.io/choff3/letterboxd-sync:latest
        environment:
            - LETTERBOXD_USERNAME=<your Letterboxd username>
            - PLEX_TOKEN=<your Plex token>
            - PLEX_HOST='http://<your Plex host>:32400'
            - BASE_URL='http://letterboxd-list:5000' # screeny05/letterboxd-list-radarr instance endpoint
            - CRON_SCHEDULE='30 * * * *' # Sets schedule for running the sync
        depends_on:
            - redis
            - letterboxd-list
    letterboxd-list:
        image: screeny05/letterboxd-list-radarr:latest
        environment:
            - REDIS_URL=redis://redis:6379
        depends_on:
            - redis
    redis:
        image: redis:6.0
```
