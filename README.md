# ChronoChat 🤖

An AI-powered chatbot with Clerk authentication, built with FastAPI, LangChain, LangGraph, and LangSmith.

## Features

- 🔐 **Clerk Authentication** - Secure user authentication and session management
  - Email/Password login
  - Google OAuth (easily configurable)
  - Support for GitHub, Discord, Facebook, and more
  - Magic links and OTP
- 🤖 **AI Chatbot** - Powered by LangChain and LangGraph
- 📊 **LangSmith Integration** - AI conversation tracing and monitoring
- 🐳 **Fully Dockerized** - Easy deployment with Docker Compose
- 🚀 **FastAPI Backend** - High-performance async API
- 🔄 **Redis Caching** - Fast response times
- 🗄️ **PostgreSQL Database** - Persistent data storage

## Tech Stack

- **Backend**: FastAPI, Python 3.11
- **AI/ML**: LangChain, LangGraph, LangSmith
- **Authentication**: Clerk
- **Database**: PostgreSQL
- **Caching**: Redis
- **Containerization**: Docker, Docker Compose

## Prerequisites

- Docker and Docker Compose
- Clerk account ([clerk.com](https://clerk.com))
- OpenAI API key (for LangChain)
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

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# LangSmith Configuration (optional)
LANGCHAIN_API_KEY=your_langsmith_api_key_here
```

### 3. Get Clerk Credentials

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

### 4. Run with Docker

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
- `POST /api/chat/message` - Send message to AI chatbot
- `GET /api/chat/conversations` - Get user's conversations
- `GET /api/chat/conversations/{conversation_id}` - Get specific conversation
- `DELETE /api/chat/conversations/{conversation_id}` - Delete conversation

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

## Next Steps

1. **Implement LangChain Integration**: Uncomment and configure LangChain in `chat_service.py`
2. **Add Database Models**: Create SQLAlchemy models for conversation persistence
3. **Implement LangGraph Workflows**: Add complex AI workflows using LangGraph
4. **Frontend Integration**: Build a frontend with React/Next.js and integrate Clerk
5. **Add Rate Limiting**: Implement rate limiting for API endpoints
6. **Add WebSocket Support**: Real-time chat with WebSocket connections

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
