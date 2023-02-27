import feedparser
import requests
from bs4 import BeautifulSoup
import re

guid = ""

def getLatestRelease():
    global guid
    
    websiteFeed = feedparser.parse("https://subsplease.org/rss/?t&r=1080")
    if websiteFeed.bozo == True:
        return
    data = websiteFeed.entries[0]
    # title = re.search("(?<=SubsPlease] )(.*)(?= -)", data['title'])
    # episode = re.search(r"\b(?:e(?:p(?:isode)?)?|x)?\s*(\d{2,3})\b", data.title)[0]
    title = data['tags'][0]['term'].split(' - 1080')[0]
    if guid != data.guid:
        guid = data.guid
        return {"latest": True, 'provider': 'subsplease', "data" : 
            {'title' : title,
            'idmal': None, 
            'link': data['link']
            }}
    else:
        return {"latest": False, 'provider': 'subsplease', "data": None}

def getFromAnimeName(anime_name):
    websiteFeed = feedparser.parse("https://subsplease.org/rss/?t")
    if websiteFeed.bozo == True:
        return

    data = websiteFeed.entries
    match = []
    for x in data:
        if anime_name in x.title:
            kualitas = re.search(r'(?<=\()(.*)(?=\))', x.title)[0]
            match.append({"title": x.title, 'kualitas': kualitas, "link": x.link})
    if match != []:
        return match

def get_schedule():
    req = requests.get('https://subsplease.org/api/?f=schedule&tz=Asia/Jakarta').json()
    all_anime = []
    for day in req['schedule']:
        for anime in req['schedule'][day]:
            if anime['title'] not in all_anime:
                all_anime.append(anime['title'])
    return all_anime

def check_airing(title):
    all_schedule = get_schedule()
    if title in all_schedule:
        return True
    else:
        return False
