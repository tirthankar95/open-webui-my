from router import ChainRouter
from uuid import uuid4
from fastapi import (
    FastAPI,
    Request
)
from starlette.responses import StreamingResponse
import json
from time import time 

app = FastAPI(
    title = "TM API",
    docs_url = "/docs",
    redoc_url = None, # Disable ReDoc
)
active_sessions = {}
router = ChainRouter()
SYSTEM_FINGERPRINT = "fp_129a36352a"

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
    last_message = messages[-1] if messages else None
    last_query = last_message.get("content", "") if last_message else ""
    
    chat_id = str(uuid4())
    chat_time = int(time())
    active_sessions[chat_id] = last_query
    
    async def event_stream():
        nonlocal chat_id 
        full_response = router.call_chain(active_sessions[chat_id])
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
    
    return StreamingResponse(event_stream(), \
                             headers={"Content-Type": "text/event-stream"})