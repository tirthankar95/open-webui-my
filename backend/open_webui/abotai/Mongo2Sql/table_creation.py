'''
Create swagger api that takes artifact-id 
and converts MongoQuery to SQL.
'''
from fastapi import (
    FastAPI
)
from Mongo2Sql.mongo_read import ReadMongo
from Mongo2Sql.deepx_sql import create_chat_table
from uuid import uuid4
import logging 
logging.getLogger(__name__)

app = FastAPI()

@app.get("/artifacts/{artefact_id}")
async def test_conversion(artefact_id: str):
    mongo_db = ReadMongo()
    artefact = mongo_db.fetch(artefact_id)
    create_chat_table(str(uuid4()), artefact)
    return {"status": 200}

def convert(chat_id: str, artefact_id: str):
    mongo_db = ReadMongo()
    artefact = mongo_db.fetch(artefact_id)
    create_chat_table(chat_id, artefact)

