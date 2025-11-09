# ChronoChat 🤖

An AI-powered chatbot with Clerk authentication, built with FastAPI, LangChain, LangGraph, and LangSmith.

## Features

- 🔐 **Clerk Authentication** - Secure user authentication and session management
  - Email/Password login
  - Google OAuth (easily configurable)
  - Support for GitHub, Discord, Facebook, and more
  - Magic links and OTP
- 🤖 **AI Chatbot** - Powered by LangChain and **LangGraph**
  - **LangGraph Agent**: State-based conversation management
  - **Google Gemini 2.0 Flash** support (fast and efficient)
  - **OpenAI GPT-4** support
  - Easy provider switching via configuration
- 📊 **LangSmith Integration** - AI conversation tracing and monitoring
- 🐳 **Fully Dockerized** - Easy deployment with Docker Compose
- 🚀 **FastAPI Backend** - High-performance async API
- �️ **Hybrid Database Architecture**:
  - **MongoDB**: Chat conversations and messages (scalable, flexible)
  - **PostgreSQL**: User data, analytics, usage stats (relational)
  - **Redis**: Caching and rate limiting
- 📦 **Repository Pattern**: Clean separation of data access logic

## Tech Stack

- **Backend**: FastAPI, Python 3.11
- **AI/ML**: LangChain, LangGraph (state-based agents), LangSmith
- **Authentication**: Clerk
- **Databases**: 
  - MongoDB (conversations/messages)
  - PostgreSQL (user data/analytics)
  - Redis (caching)
- **ORM/ODM**: SQLAlchemy (async), Motor (async MongoDB)
- **Migrations**: Alembic
- **Containerization**: Docker, Docker Compose

## Prerequisites

- Docker and Docker Compose
- Clerk account ([clerk.com](https://clerk.com))
- **AI Provider** (choose one):
  - Google Gemini API key (recommended, free tier available)
  - OpenAI API key
- LangSmith account (optional, for tracing)

## Setup

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd ChronoChat
```

### 2. Configure environment variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Update the following variables in `.env`:

```env
# Clerk Configuration
CLERK_PUBLISHABLE_KEY=pk_test_your_key_here
CLERK_SECRET_KEY=sk_test_your_key_here
CLERK_JWT_KEY=your_jwt_key_here

# AI Provider (choose one)
AI_PROVIDER=gemini  # Options: gemini, openai

# Google Gemini Configuration (if using Gemini)
GOOGLE_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp

# OpenAI Configuration (if using OpenAI)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4

# LangSmith Configuration (optional)
LANGCHAIN_API_KEY=your_langsmith_api_key_here
```

### 3. Get AI Provider API Key

#### Option A: Google Gemini (Recommended)
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy the API key → `GOOGLE_API_KEY`
4. Set `AI_PROVIDER=gemini` in `.env`

#### Option B: OpenAI
1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create new API key
3. Copy the API key → `OPENAI_API_KEY`
4. Set `AI_PROVIDER=openai` in `.env`

### 4. Get Clerk Credentials

1. Go to [clerk.com](https://clerk.com) and create an account
2. Create a new application
3. **Enable Google Authentication (Optional)**:
   - In Clerk Dashboard, go to **User & Authentication** → **Social Connections**
   - Toggle on **Google**
   - Configure OAuth settings (Clerk provides test credentials, or use your own Google OAuth app)
   - You can also enable other providers: GitHub, Facebook, Discord, etc.
4. Go to **API Keys** section
5. Copy:
   - Publishable Key → `CLERK_PUBLISHABLE_KEY`
   - Secret Key → `CLERK_SECRET_KEY`
6. For JWT Key, go to **JWT Templates** and create a template, then copy the PEM public key → `CLERK_JWT_KEY`

### 5. Run with Docker

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

The API will be available at:
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

## Development (Without Docker)

### 1. Create virtual environment

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows PowerShell
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the application

```bash
python -m uvicorn app.main:app --reload
```

## API Endpoints

### Health Check
- `GET /api/health` - Health check
- `GET /api/ready` - Readiness check

### Authentication (Protected)
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/verify` - Verify authentication token
- `GET /api/auth/session/{session_id}` - Verify session

### Chat (Protected)
- `POST /api/chat/message` - Send message to AI chatbot (LangGraph agent)
- `GET /api/chat/conversations` - Get user's conversations (from MongoDB)
- `GET /api/chat/conversations/{conversation_id}` - Get specific conversation
- `DELETE /api/chat/conversations/{conversation_id}` - Delete conversation
- `GET /api/chat/search?q=query` - Search conversations

### System
- `GET /api/system/ai-provider` - Get current AI provider info

## Authentication

All protected endpoints require a Bearer token in the Authorization header:

```bash
curl -H "Authorization: Bearer YOUR_CLERK_TOKEN" \
     http://localhost:8000/api/auth/me
```

## Project Structure

```
ChronoChat/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── api/
│   │   └── routes/
│   │       ├── auth.py         # Auth endpoints
│   │       ├── chat.py         # Chat endpoints
│   │       └── health.py       # Health checks
│   ├── core/
│   │   ├── config.py           # Configuration
│   │   └── clerk.py            # Clerk auth utilities
│   └── services/
│       └── chat_service.py     # Chat service (LangChain)
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

## Switching AI Providers

The application supports both Google Gemini and OpenAI. To switch:

### Use Gemini (Default)
```env
AI_PROVIDER=gemini
GOOGLE_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.0-flash-exp
```

### Use OpenAI
```env
AI_PROVIDER=openai
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4
```

Check current provider:
```bash
curl http://localhost:8000/api/system/ai-provider
```

## Database Migrations

### Initialize Database (First Time)
```bash
# Create initial migration
docker-compose exec api alembic revision --autogenerate -m "Initial migration"

# Apply migrations
docker-compose exec api alembic upgrade head
```

### After Model Changes
```bash
# Generate migration
docker-compose exec api alembic revision --autogenerate -m "Description of changes"

# Apply migration
docker-compose exec api alembic upgrade head
```

See [DATABASE_ARCHITECTURE.md](DATABASE_ARCHITECTURE.md) for detailed database design.

## Next Steps

1. ✅ **AI Integration Complete** - Gemini and OpenAI support ready
2. ✅ **LangGraph Agent Implemented** - State-based conversation management
3. ✅ **MongoDB Integration** - Chat storage with conversation repository
4. ✅ **PostgreSQL Models** - User data, analytics, usage tracking
5. ✅ **Hybrid Database Architecture** - Best of both worlds
6. **Frontend Integration**: Build a frontend with React/Next.js and integrate Clerk
7. **Implement User Analytics**: Track usage stats and sessions
8. **Add Rate Limiting**: Implement rate limiting for API endpoints
9. **Add WebSocket Support**: Real-time chat with WebSocket connections
10. **Advanced LangGraph Workflows**: Multi-agent systems, tool usage

## Docker Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f api

# Rebuild
docker-compose up -d --build

# Remove volumes (reset database)
docker-compose down -v
```

## Troubleshooting

### Issue: Authentication fails
- Verify your Clerk keys in `.env`
- Ensure JWT key is correctly formatted (PEM format)
- Check token expiration

### Issue: Database connection fails
- Ensure PostgreSQL container is running: `docker-compose ps`
- Check database credentials in `.env`

### Issue: Redis connection fails
- Ensure Redis container is running
- Check Redis URL in `.env`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License
