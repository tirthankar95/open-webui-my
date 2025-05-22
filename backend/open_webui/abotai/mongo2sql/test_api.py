'''
Create swagger api that takes artifact-id 
and converts MongoQuery to SQL.
'''
from fastapi import (
    FastAPI
)
from mongo2sql.mongo_read import ReadMongo
from mongo2sql.sql_write import InsertLog
import logging 
logging.getLogger(__name__)

app = FastAPI()
mongo_db = ReadMongo()
sql_db = InsertLog()

@app.get("/artifacts/{artefact_id}")
async def get_artifact(artefact_id: str):
    artefact = mongo_db.fetch(artefact_id)
    # PCAP
    for doc in artefact:
        if "pcap" in doc and "prompt" in doc["pcap"]:
            sql_db.start(doc['pcap']['prompt'])
        break
    return {"status": 200}