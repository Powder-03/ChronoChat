# ChronoChat Backend

A modern FastAPI backend for the ChronoChat application with authentication, chat functionality, and Redis session management.

## Features

- **Authentication System**: Complete auth with JWT tokens, refresh tokens, and session management
- **User Management**: Registration, login, logout, profile management
- **Chat System**: Thread-based conversations with message history
- **Database Integration**: PostgreSQL with SQLAlchemy ORM and async support
- **Session Management**: Redis-based session storage for fast access
- **Security**: Password hashing, token validation, and secure session handling
- **API Documentation**: Automatic OpenAPI/Swagger documentation

## Project Structure

```
Backend/
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── auth.py          # Authentication endpoints
│   │       ├── chat.py          # Chat endpoints
│   │       └── users.py         # User management endpoints
│   ├── core/
│   │   ├── config.py            # Application configuration
│   │   ├── database.py          # Database connection and setup
│   │   ├── redis.py             # Redis client configuration
│   │   └── security.py          # Security utilities (JWT, password hashing)
│   ├── models/
│   │   ├── user.py              # User and session models
│   │   └── chat.py              # Chat thread and message models
│   ├── schemas/
│   │   ├── auth.py              # Authentication request/response schemas
│   │   └── chat.py              # Chat request/response schemas
│   ├── services/
│   │   ├── auth.py              # Authentication business logic
│   │   └── chat.py              # Chat business logic
│   └── utils/
│       └── dependencies.py      # FastAPI dependencies
├── main.py                      # Application entry point
├── requirements.txt             # Python dependencies
└── .env.example                 # Environment variables example
```

## Setup Instructions

### 1. Prerequisites

- Python 3.10+
- PostgreSQL database
- Redis server

### 2. Installation

```bash
# Clone the repository
cd Backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your configurations
nano .env
```

### 4. Database Setup

```bash
# Create PostgreSQL database
createdb chronochat

# Update DATABASE_URL in .env file
DATABASE_URL=postgresql://username:password@localhost/chronochat
```

### 5. Run the Application

```bash
# Start the FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/logout` - Logout current session
- `POST /api/auth/logout-all` - Logout all sessions
- `GET /api/auth/me` - Get current user info
- `GET /api/auth/verify` - Verify token validity

### Chat
- `POST /api/chat/send` - Send chat message
- `GET /api/chat/threads` - Get user's chat threads
- `GET /api/chat/threads/{thread_id}` - Get thread history
- `DELETE /api/chat/threads/{thread_id}` - Delete chat thread
- `PUT /api/chat/threads/{thread_id}/title` - Update thread title
- `GET /api/chat/stats` - Get user chat statistics

### Users
- `GET /api/users/profile` - Get user profile
- `PUT /api/users/profile` - Update user profile
- `POST /api/users/change-password` - Change password
- `DELETE /api/users/account` - Delete/deactivate account

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Development

### Code Structure

The application follows a clean architecture pattern:

1. **Routes**: Handle HTTP requests and responses
2. **Services**: Contain business logic
3. **Models**: Define database schemas
4. **Schemas**: Define request/response validation
5. **Utils**: Shared utilities and dependencies

### Security Features

- Password hashing with bcrypt
- JWT access and refresh tokens
- Session management with Redis
- Token expiration and validation
- Rate limiting (configurable)
- CORS protection

### Database Models

- **User**: User accounts and authentication data
- **UserSession**: Active user sessions
- **ChatThread**: Chat conversation threads
- **ChatMessage**: Individual chat messages
- **ToolCall**: AI tool usage tracking

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379` |
| `SECRET_KEY` | JWT signing key | Required |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime | `30` |
| `DEBUG` | Debug mode | `False` |
| `CORS_ORIGINS` | Allowed CORS origins | `["http://localhost:3000"]` |

## Production Deployment

1. Set `DEBUG=False` in environment
2. Use a strong `SECRET_KEY`
3. Configure proper database and Redis instances
4. Set up reverse proxy (Nginx)
5. Use HTTPS
6. Configure logging and monitoring

## Contributing

1. Follow PEP 8 style guidelines
2. Add type hints to all functions
3. Write tests for new features
4. Update documentation as needed

## License

This project is part of the ChronoChat application.
