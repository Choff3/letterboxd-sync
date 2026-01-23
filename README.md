# letterboxd-sync

This a Python script that grabs a [Letterboxd](https://letterboxd.com) watchlist using https://github.com/screeny05/letterboxd-list-radarr and then adds the movies from that list to your [Plex](https://www.plex.tv/) watchlist.

## Getting API Token
### Plex
https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/

## Sample run command
```
docker run --rm \
    -e LETTERBOXD_USERNAME='{Letterboxd username}' \
    -e PLEX_TOKEN='{Plex token}' \
    -e PLEX_HOST='http://{Plex server's IP}:32400' \
    -e BASE_URL='http://localhost:5000' \ # optional local hosted version of screeny05/letterboxd-list-radarr
    choff3/letterboxd-sync
```