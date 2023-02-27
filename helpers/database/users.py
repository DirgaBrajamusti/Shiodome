from helpers.database.database import database

def create_user(user_id):
    db = database()
    data = { "id": user_id, "Name": user_id }
    result = db['users'].insert_one(data)
    return result

def check_user(user_id):
    db = database()
    users = db['users']
    results = users.find_one({'id': user_id}, {"provider"})
    print(type(results))
    if results != None:
        return {"status": True, "data":results}
    return {"status": False, "data" : {}}
