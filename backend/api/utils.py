# backend/api/utils.py
import json
import redis

def get_conversation_history(user_id: str, conversation_id: str, redis_client: redis.Redis) -> list:
    """Retrieve conversation history for a user and conversation_id from Redis."""
    history_key = f"history:{user_id}:{conversation_id}"
    history_data = redis_client.get(history_key)
    if history_data:
        return json.loads(history_data.decode('utf-8'))
    return []

def store_conversation(user_id: str, conversation_id: str, user_message: str, bot_response: str, redis_client: redis.Redis):
    """Store a new conversation entry for a user in Redis."""
    history_key = f"history:{user_id}:{conversation_id}"
    conv_ids_key = f"conversations:{user_id}"
    
    # Fetch existing history
    history = get_conversation_history(user_id, conversation_id, redis_client)
    history.append({"user": user_message, "bot": bot_response})
    
    # Store updated history
    redis_client.set(history_key, json.dumps(history))
    redis_client.expire(history_key, 3600)  # Expire after 1 hour (optional)
    
    # Add conversation_id to user's set of conversations
    redis_client.sadd(conv_ids_key, conversation_id)
    redis_client.expire(conv_ids_key, 3600)  # Expire after 1 hour (optional)