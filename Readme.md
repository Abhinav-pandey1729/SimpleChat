# SimpleChat: LLM-Powered Chatbot

## Overview
SimpleChat is a lightweight, scalable chatbot powered by GPT-4o-mini (via OpenAI API), designed to support 10,000+ users. It features a modern React frontend with an intuitive chat UI, a FastAPI backend with Redis for caching and conversation history management, and an ML pipeline to enhance response quality and reduce hallucinations. Developed through iterative collaboration, this project showcases a robust integration of machine learning capabilities with a focus on scalability, reliability, and cost efficiency.

## System Architecture
- **Frontend**: React-based interface with real-time messaging, emoji support, and chat history management.
- **Backend**: FastAPI for API endpoints, integrating GPT-4o-mini and Redis for caching and persistence.
- **LLM**: GPT-4o-mini via OpenAI API for natural language generation.
- **Cache/Storage**: Redis for caching responses (1-hour TTL) and storing conversation histories.
- **ML Pipeline**: Context-aware response generation with hallucination mitigation.

## Development Process
- **Initial Setup**: Created a GitHub repository (`https://github.com/Abhinav-pandey1729/SimpleChat`) and initialized a local Git repository to manage code versioning.
- **Backend Development**: Implemented FastAPI endpoints (`/chat`, `/history`, `/new-conversation`) with OpenAI integration, Redis caching, and logging for debugging.
- **Frontend Development**: Built a React-based chat interface with components like `ChatWindow.js` and `ChatWindow.css`, supporting new chat creation, message sending, and history retrieval.
- **Issue Resolution**: Addressed bugs (e.g., pre-filled "New conversation started" messages, auto-loading last chat on login) through iterative code updates and testing.
- **Styling Adjustments**: Modified CSS to reduce dialog box opacity and align with a black background, enhancing user experience.
- **Deployment Preparation**: Configured `.gitignore` to exclude `node_modules`, `*.pyc`, and `chatbot.log`, and added a comprehensive `README.md`.

## Novel Approaches to Improve Response Quality or Reduce Hallucinations
- **Contextual Memory with Redis**: Leverages Redis to store conversation history, ensuring the LLM maintains context across messages, reducing irrelevant or hallucinated responses.
- **Caching Strategy**: Implements a 1-hour TTL cache for frequent queries, minimizing redundant API calls to OpenAI and stabilizing response consistency.
- **Hallucination Mitigation**: Introduces a system prompt with strict guidelines (e.g., avoiding humor unless required, no explicit language) to guide GPT-4o-mini toward factual and appropriate responses. Future enhancements could include a lightweight validation layer to flag and correct hallucinated outputs using rule-based checks or a secondary model.
- **Dynamic Welcome Message**: Delays the welcome message until the user’s first input, allowing personalized context initiation and reducing generic responses.

## ML Pipeline Design and Implementation
- **Data Flow**:
  - **Input**: User messages are received via the React frontend and sent to the FastAPI backend.
  - **Preprocessing**: Messages are appended to the Redis-stored conversation history, maintaining context.
  - **Model Inference**: GPT-4o-mini processes the conversation history with a custom system prompt, generating responses.
  - **Postprocessing**: Responses are cached in Redis, logged, and returned to the frontend.
- **Implementation**:
  - **Backend**: `main.py` handles API logic, `utils.py` manages Redis interactions, and `constants.py` stores API keys (to be moved to environment variables).
  - **Frontend**: `ChatWindow.js` manages UI state and API calls, with `ChatWindow.css` styling the interface.
- **Scalability**: The pipeline supports parallel backend instances, with Redis distributing load.

## Documentation of ML System Design Decisions
- **Model Choice**: GPT-4o-mini was selected for its balance of performance and cost, suitable for 10,000+ users with caching support.
- **Context Management**: Redis was chosen over in-memory storage for persistence and scalability across multiple backend instances.
- **Caching TTL**: A 1-hour expiry balances response speed and relevance, avoiding stale data.
- **Prompt Engineering**: The system prompt enforces factual responses and reduces hallucinations, with potential for future refinement using fine-tuning or external validation.
- **Security**: API keys are intended to be managed via environment variables to prevent exposure in the repository.

## Overall Approach and Design Philosophy
- **Philosophy**: SimpleChat prioritizes scalability, reliability, and user experience, leveraging modern tools (React, FastAPI, Redis) with a minimalist ML integration to deliver efficient chatbot functionality.
- **Handling Required Scale (10,000+ Users)**:
  - **Horizontal Scaling**: Multiple FastAPI instances can be deployed behind a load balancer, with Redis as a shared cache and history store.
  - **Caching**: Reduces OpenAI API calls, mitigating cost and latency for high user volumes.
  - **Asynchronous Design**: Future enhancements could include async task queues (e.g., Celery) for handling spikes in traffic.
- **Key Technical Decisions and Justification**:
  - **FastAPI over Flask**: Chosen for its async capabilities and performance, supporting high concurrency.
  - **Redis over Database**: Preferred for its speed and simplicity in caching and temporary storage, avoiding the overhead of a full database.
  - **GPT-4o-mini over Larger Models**: Selected to optimize cost and response time while maintaining quality for conversational tasks.
  - **React Frontend**: Adopted for its component-based architecture and real-time UI updates, enhancing user interaction.

## Setup Instructions
1. **Prerequisites**:
   - Install Python 3.9+, Node.js, and Redis.
   - Obtain an OpenAI API key and set it as an environment variable: `export OPENAI_API_KEY=your-api-key`.
2. **Backend Setup**:
   - Navigate to `backend/`: `cd backend`.
   - Install dependencies (e.g., `pip install fastapi uvicorn openai redis`).
   - Run the server: `python -m backend.api.main` (ensure Redis is running locally on `localhost:6379`).
3. **Frontend Setup**:
   - Navigate to `frontend/`: `cd frontend`.
   - Install dependencies: `npm install`.
   - Start the app: `npm start` (runs on `http://localhost:3000`).
4. **Test**:
   - Open `http://localhost:3000` in a browser, log in with a `userId` (e.g., "Abhinav"), and start a new chat.

## Deployment Instructions or Demo Environment
- **Deployment**:
  - **Containerization**: Use Docker to package the backend and frontend.
    - Create a `Dockerfile` for the backend:
      ```dockerfile
      FROM python:3.9
      WORKDIR /app
      COPY backend/ .
      RUN pip install fastapi uvicorn openai redis
      CMD ["python", "-m", "backend.api.main"]
