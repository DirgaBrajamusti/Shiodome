import pymongo, os
from dotenv import load_dotenv

load_dotenv()

def database():
    mongo_client = pymongo.MongoClient(os.getenv("MONGO_DB"))
    mongo_database = mongo_client["RinAnime"]
    return mongo_database

