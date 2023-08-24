import os
from typing import List
from pydantic import BaseModel
import redis
import json
import logging
from langchain.memory import RedisChatMessageHistory
from langchain.schema import (
    messages_from_dict
)
import secrets

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_redis():
    r = redis.Redis(host=os.getenv('REDIS_HOST'), port=int(os.getenv('REDIS_PORT')), db=0)
    return r


class Message(BaseModel):
    role: str
    content: str


class Conversation(BaseModel):
    conversation: List[Message]


async def db_get_conversation(conversation_key: str):
    logger.info(f"Retrieving conversation history for id {conversation_key}")
    _items = get_redis().lrange(conversation_key, 0, -1)
    # print(_items)
    if _items:
        items = [json.loads(m.decode("utf-8")) for m in _items[::-1]]
        messages = messages_from_dict(items)

        # existing_conversation = await json.loads(existing_conversation_json[0])
        # return existing_conversation
        return messages
    else:
        return [{"error": "Conversation not found. Please create a new chat."}]


async def db_create_conversation(user_id: str, conversation_id: str):
    # conversation_id = secrets.token_hex(16)
    conversation_key = f"{user_id}:{conversation_id}"
    logger.info(f"Creating Conversation with ID {conversation_key}")
    _items = get_redis().lrange(conversation_key, 0, -1)
    # print(_items)
    if _items:
        return {"error": f"Conversation with {conversation_key} already exist"}
    else:
        history = RedisChatMessageHistory(key_prefix=user_id + ':', session_id=conversation_id)
        print('history.messages', len(history.messages))
        if len(history.messages) == 0:
            history.add_ai_message("Good day How can I help you today")
        return await db_get_conversation(conversation_key)

async def db_delete_conversation(conversation_key: str):
    logger.info(f"Deleting conversation history for id {conversation_key}")
    redis_instance = get_redis()
    result = redis_instance.delete(conversation_key)
    if result == 1:
        return {"success": f"Conversation with {conversation_key} deleted successfully"}
    else:
        return {"error": f"Conversation with {conversation_key} does not exist"}
