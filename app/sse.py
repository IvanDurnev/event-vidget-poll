import json
import time
from flask import Response
from app.redis import redis_client

def event_stream(poll_id):
    pubsub = redis_client.pubsub()
    pubsub.subscribe(f"chat:{poll_id}")

    for message in pubsub.listen():
        if message["type"] == "message":
            yield f"data: {json.dumps({'text': message['data']})}\n\n"