from uuid import uuid4
from fastapi import (
    FastAPI,
    Request
)
import os 
import json
from time import time 
from Chains.chain_router import ChainRouter
from Mongo2Sql.table_creation import convert
from config import (
    SQL_PATH, 
    DPX_MAIN_TABLE
)
from sqlalchemy import (
    create_engine,
    text
)
from fastapi.responses import JSONResponse
from starlette.responses import StreamingResponse
import logging 
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
)

app = FastAPI(
    title = "TM API",
    docs_url = "/docs",
    redoc_url = None, # Disable ReDoc
)
active_sessions = {}
SYSTEM_FINGERPRINT = "fp_129a36352a"
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{SQL_PATH}/webui.db")
conn = create_engine(DATABASE_URL, echo=False).connect()

def sanitize(value: str) -> str:
    value_arr = value.split("-")
    return ''.join(value_arr)

def create_table(chat_id: str, job_id: str):
    '''
    Create the tales if it doesn't exist. 
    '''
    global conn
    resp = conn.execute(text(f"PRAGMA table_info({DPX_MAIN_TABLE + chat_id});")).fetchall()
    if not resp:
        logging.info(f"Creating tables: [{DPX_MAIN_TABLE + chat_id}]")
        convert(chat_id, job_id)

@app.post("/chat/completions")
async def root(request: Request):
    global active_sessions
    '''
    Returns a coroutine (won’t work unless awaited)
    The request object reads the incoming body from an async stream, 
    so operations like parsing JSON from the body are I/O-bound and must be awaited.
    '''
    payload = await request.json()
    model_name = payload.get("model", "")
    messages = payload.get("messages", [])
    metadata = payload.get("metadata", {})

    chat_id = sanitize(metadata.get("chat_id", "x"))
    job_id = sanitize(metadata.get("job_id", "2ff53e5525184d25959704498f044fe7"))
    chat_time = int(time())
    create_table(chat_id, job_id)
    if chat_id not in active_sessions:
        # Create a new rounter for chat_id if it doesn't exist in memory.
        active_sessions[chat_id] = ChainRouter(chat_id)
    
    async def event_stream():
        nonlocal chat_id 
        full_response = active_sessions[chat_id].call_chain(messages, [])
        for token in full_response.split(" "):
            json_data = {
                "id": f"chatcmpl-{chat_id}",
                "object": "chat.completion.chunk",
                "created": f"{chat_time}",
                "model": f"{model_name}",
                "service_tier": "default",
                "system_fingerprint": f"{SYSTEM_FINGERPRINT}",
                "choices": [{
                    "index": 0,
                    "delta": {"content": f"{token} "},
                    "logprobs": None,
                    "finish_reason": None
                }]
            }
            yield f"data: {json.dumps(json_data)}\n\n"
        json_data = {
            "id": f"chatcmpl-{chat_id}",
            "object": "chat.completion.chunk",
            "created": f"{chat_time}",
            "model": f"{model_name}",
            "service_tier": "default",
            "system_fingerprint": f"{SYSTEM_FINGERPRINT}",
            "choices": [{
                "index": 0,
                "delta": {"content": ""},
                "logprobs": None,
                "finish_reason": "stop"
            }]
        }
        yield f"data: {json.dumps(json_data)}\n\n"
    
    async def event():
        nonlocal chat_id
        full_response = active_sessions[chat_id].call_chain(messages, [])
        json_data = {
            "id": f"chatcmpl-{chat_id}",
            "object": "chat.completion.chunk",
            "created": f"{chat_time}",
            "model": f"{model_name}",
            "choices": [
                {
                    "index": 0,
                    "message":{
                        "role": "ai",
                        "content": f"{full_response}",
                        "refusal": None,
                        "annotations": []
                    },
                    "logprobs": None,
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": -1,
                "completion_tokens": -1,
                "total_tokens": -1,
                "prompt_tokens_details": {
                "cached_tokens": -1,
                "audio_tokens": -1
                },
            },
            "completion_tokens_details": {
                "reasoning_tokens": -1,
                "audio_tokens": -1,
                "accepted_prediction_tokens": -1,
                "rejected_prediction_tokens": -1
                },
            "service_tier": "default",
        }
        return json_data

    if payload.get('stream', False):
        return StreamingResponse(event_stream(), \
                                headers={"Content-Type": "text/event-stream"})
    else:
        return JSONResponse(content = await event())