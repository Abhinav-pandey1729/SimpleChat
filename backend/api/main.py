# backend/api/main.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
import redis
from typing import List, Dict
from backend.api.constants import OPENAI_API_KEY
from backend.api.utils import get_conversation_history, store_conversation
import logging
import datetime
import uuid

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("chatbot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI
openai.api_key = OPENAI_API_KEY

# Initialize Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)

class ChatRequest(BaseModel):
    user_id: str
    message: str
    conversation_id: str = None  # Optional conversation_id for new sessions

class ChatResponse(BaseModel):
    response: str
    conversation_id: str

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        logger.info(f"Received request from user {request.user_id}: {request.message}")

        # Generate a new conversation_id if none provided
        conversation_id = request.conversation_id or str(uuid.uuid4())

        # Fetch conversation history from Redis
        history = get_conversation_history(request.user_id, conversation_id, redis_client)
        logger.debug(f"Conversation history for {request.user_id} (conv_id: {conversation_id}): {history}")

        # System prompt
        messages = [
            {
                "role": "system",
                "content": "You are a smart and witty AI assistant named Steve. You were created by Abhinav Pandey from IIT Kanpur. Respond with dry humor, clever quips, and a bit of attitude, but keep it friendly. Avoid being overly rude or offensive. Know when to bring in Sarcasm and when to keep it neat and without any overdue information. If there is a pointed question, just answer it simply in a few words. Do not use any explicit language in any answer even if the user insists to. Give humor only when required. If there is a specific question regarding anything, give that specific reply without the funny business."
            }
        ]
        for entry in history:
            messages.append({"role": "user", "content": entry["user"]})
            messages.append({"role": "assistant", "content": entry["bot"]})
        messages.append({"role": "user", "content": request.message})

        # Add welcome message for the first message in a new conversation
        if not history:
            messages.append({"role": "assistant", "content": "Hello! I’m Steve, your witty AI assistant. What’s on your mind today?"})

        # Check cache
        cache_key = f"response:{request.user_id}:{request.message}:{conversation_id}"
        cached_response = redis_client.get(cache_key)
        if cached_response:
            logger.info(f"Cache hit for {request.user_id}: {request.message}")
            return ChatResponse(response=cached_response.decode(), conversation_id=conversation_id)

        # Generate response
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=150,
            temperature=0.6
        )
        bot_response = response.choices[0].message["content"].strip()

        logger.info(f"Generated response for {request.user_id}: {bot_response}")

        # Cache response (1 hour expiry)
        redis_client.setex(cache_key, 3600, bot_response)

        # Store conversation in Redis
        logger.debug(f"Storing conversation for {request.user_id}: user={request.message}, bot={bot_response}")
        store_conversation(request.user_id, conversation_id, request.message, bot_response, redis_client)
        logger.debug(f"Stored history for {request.user_id}: {get_conversation_history(request.user_id, conversation_id, redis_client)}")

        return ChatResponse(response=bot_response, conversation_id=conversation_id)
    except Exception as e:
        logger.error(f"Error processing request for {request.user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history/{user_id}")
async def get_history(user_id: str):
    try:
        # Fetch all conversation IDs for the user
        conv_ids_key = f"conversations:{user_id}"
        conversation_ids = redis_client.smembers(conv_ids_key)
        conversation_ids = [cid.decode('utf-8') for cid in conversation_ids] if conversation_ids else []

        # Fetch history for each conversation
        history = []
        for conv_id in conversation_ids:
            conv_history = get_conversation_history(user_id, conv_id, redis_client)
            if conv_history:
                # Use the first user message as the summary
                summary = conv_history[0]["user"][:50] + "..." if len(conv_history[0]["user"]) > 50 else conv_history[0]["user"]
                history.append({
                    "conversation_id": conv_id,
                    "summary": summary,
                    "messages": conv_history
                })

        logger.info(f"Retrieved history for {user_id}: {history}")
        return {"history": history}
    except Exception as e:
        logger.error(f"Error retrieving history for {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/new-conversation/{user_id}")
async def new_conversation(user_id: str):
    """Create a new conversation for the user without pre-filling messages."""
    try:
        conversation_id = str(uuid.uuid4())
        logger.info(f"Created new conversation for {user_id} with ID: {conversation_id}")
        return {"conversation_id": conversation_id}
    except Exception as e:
        logger.error(f"Error creating new conversation for {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)