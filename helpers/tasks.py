import requests
import datetime
import logging

from helpers.scrapers import subsplease
from helpers.database import webhook, anime
logger = logging.getLogger('app.task')

def send_discord_webhook(url, title, field, value):
    url = url

    data = {
        "username" : "./Shiodome"
    }

    data["embeds"] = [
        {
        "title": f":newspaper: | {title}",
        "color": 388095,
        "fields": [
            {
            "name": field,
            "value": value
            }
        ],
        "footer": {
            "text": "Shiodome v.0.0.1"
        },
        "timestamp": datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        }
    ]

    result = requests.post(url, json = data)

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        logger.critical(err)
    else:
        logger.info('[Discord] Webhook sended')

def anime_task():
    print("[RSS] Check")
    logger.info("[Anime RSS] Check")
    for releases in [subsplease.getLatestRelease()]:
        if releases['latest'] == True:
            logger.info('[Anime RSS] New Release')
            print('[Anime RSS] New Release')
            title = releases['data']['title']
            provider = releases['provider']
            link = releases['data']['link']
            
            user_watchlist_data = anime.get_user_from_anime_name(title)
            if user_watchlist_data['status']:
                for user_id in user_watchlist_data['data']:
                    if provider == 'subsplease':
                        links = []
                        for release in subsplease.getFromAnimeName(title):
                            links.append(f'[{release["kualitas"]}]({release["link"]})')
                        all_links = " | ".join(links)
                        webhook_url_data = webhook.get_url(user_id['id'])
                        for webhook_url in webhook_url_data['data']:
                            if webhook_url["webhook"] == 'discord':
                                send_discord_webhook(webhook_url["url"], title, provider, all_links)