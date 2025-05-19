'''
Create swagger api that takes artifact-id 
and converts MongoQuery to SQL.
'''
from fastapi import (
    FastAPI
)
from mongo_read import ReadMongo
from sql_write import InsertLog
import logging 
logging.getLogger(__name__)

app = FastAPI()
mongo_db = ReadMongo(db_name="LLMQueryAgent", collection_name="Functional")
sql_db = InsertLog()

@app.get("/artifacts/{artifact_id}")
async def get_artifact(artifact_id: str):
    artifact = mongo_db.fetch(artifact_id)
    for doc in artifact: 
        if "_id" in doc:
            doc["_id"] = str(doc["_id"])
    sql_db.start(artifact)
    return {"status": 200}