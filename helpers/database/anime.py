from helpers.database.database import database
import logging

logger = logging.getLogger('app')

def add_watchlist(user_id, provider, anime_name):
    db = database()
    data = { "id": user_id.lower(), "provider": provider.lower(), "anime_name": anime_name}
    result = db['watchlist'].insert_one(data)
    return result

def get_watchlist(user_id):
    db = database()
    logger.info('Utility function called')
    query = db['watchlist'].find({"id": user_id}, {"_id": 1, "id": 1, "provider": 1, "anime_name": 1})
    results = list(query)
    if len(results) != 0:
        return {"status": True, "data": results}
    return {"status": False, "data": []}

def get_user_from_anime_name(anime_name):
    db = database()
    query = db['watchlist'].find({'anime_name': anime_name}, {"id": 1, "provider": 1, "anime_name": 1})
    results = list(query)
    if len(results) != 0:
        return {"status": True, "data": results}
    return {"status": False, "data": []}

def delete_watchlist(user_id, provider, anime_name):
    db = database()
    watchlist = db['watchlist']
    query = { "id": user_id, "provider": provider, "anime_name": anime_name}
    result = watchlist.delete_one(query)
    return result
