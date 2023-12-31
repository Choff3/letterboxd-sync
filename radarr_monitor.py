import requests
import os

def radarr_monitor_add(radarr_films,host_url,api_key):

    root_dir = requests.get(host_url+'/api/v3/rootfolder', params={"apikey": api_key}).json()[0]['path']

    for tmdbid in radarr_films:
        try:
            movie = requests.get(host_url+'/api/v3/movie/lookup/tmdb?tmdbId='+tmdbid, params={"apikey": api_key}).json()

            movie["QualityProfileId"] = 1
            movie["rootFolderPath"] = root_dir
            movie["monitored"] = True
            movie["searchOnAdd"] = True

            requests.post(host_url+'/api/v3/movie', params={"apikey": api_key}, json=movie)
            print("Monitored tmdb://"+tmdbid+" on Radarr")
        except:
            print("tmdb://"+tmdbid+" not added to Radarr")