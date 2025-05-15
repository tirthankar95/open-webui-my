'''
Connect to MongoDB and return 
all data with an artifact id.
'''
from pymongo import MongoClient 
from typing import Union
import logging 
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - [%(levelname)s] - %(filename)s:%(lineno)d: %(message)s",
    handlers=[
        logging.StreamHandler() # logs to stdout
    ]
)

class ReadMongo:
    def __init__(self, host: str = "localhost", port: int = 27017, \
                 db_name: Union[str, None] = None, collection_name: Union[str, None] = None):
        ## MongoDB collection
        self.client = MongoClient(f"mongodb://{host}/{port}")
        self.collection = self.client[db_name][collection_name]
    
    def fetch(self, artifact_id: str):
        query = {"job_id": artifact_id}
        return list(self.collection.find(query))

        