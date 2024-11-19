from pymongo import MongoClient 
from app.core.config import Config

def get_db():
    client = MongoClient(Config.MONGO_URI)
    collection = client['sprint-hsl']
    db = collection['users']
    return db