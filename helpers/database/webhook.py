from helpers.database.database import database

def add_webhook(user_id, webhook, url):
    db = database()
    data = { "id": user_id.lower(), "webhook": webhook.lower(), "url": url}
    result = db['webhook'].insert_one(data)
    return result

def get_url(user_id):
    db = database()
    users = db['webhook']
    query = users.find({'id': user_id})
    results = list(query)
    if results != None:
        return {"status": True, "data": results}
    return {"status": False, "data" : {}}