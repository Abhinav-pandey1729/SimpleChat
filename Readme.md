# SimpleChat: LLM-Powered Chatbot

## Overview
SimpleChat is a lightweight chatbot powered by GPT-4o-mini (via OpenAI API), designed to support 10,000+ users. It features a modern React frontend and a FastAPI backend with Redis for caching and conversation history.

## System Architecture
- **Frontend**: React with a clean, modern chat UI.
- **Backend**: FastAPI for API endpoints and GPT-4o-mini integration.
- **LLM**: GPT-4o-mini via OpenAI API.
- **Cache/Storage**: Redis for caching responses and storing conversation history.

## Setup Instructions
1. Follow the step-by-step guide below to set up and run the application.

## Scalability
- **10,000+ Users**: Redis caching and queuing handle load. Run multiple backend instances for horizontal scaling.

## Reliability
- **Failures**: Stateless backend with Redis persistence.

## Cost Considerations
- **Caching**: Reduces OpenAI API calls.

## ML/AI Integration
- **LLM**: GPT-4o-mini via OpenAI API.
- **Context Management**: Redis for conversation history.