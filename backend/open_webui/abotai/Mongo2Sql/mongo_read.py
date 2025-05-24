'''
Connect to MongoDB and return 
all data with an artifact id.
'''
from pymongo import MongoClient 
from config import (
    MONGO_HOST, 
    MONGO_PORT,
    MONGO_COLLECTION,
    MONGO_DOCUMENT
)
import logging 
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - [%(levelname)s] - %(filename)s:%(lineno)d: %(message)s",
    handlers=[
        logging.StreamHandler() # logs to stdout
    ]
)

class ReadMongo:
    def __init__(self):
        ## MongoDB collection
        self.client = MongoClient(f"mongodb://{MONGO_HOST}:{MONGO_PORT}/")
        self._collection = self.client[MONGO_COLLECTION][MONGO_DOCUMENT]
    
    def fetch(self, artifact_id: str):
        query = {"job_id": artifact_id}
        return list(self._collection.find(query))
    

if __name__ == '__main__':
    robj = ReadMongo()
    print(robj.fetch("2ff53e5525184d25959704498f044fe7"))