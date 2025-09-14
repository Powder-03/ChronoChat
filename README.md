# ChronoChat

A modern, AI-powered chat application built with FastAPI backend, Streamlit frontend, and LangGraph for advanced conversation management. ChronoChat offers intelligent conversations with tool integration, web search capabilities, and both normal and RAG (Retrieval-Augmented Generation) modes.

## 🚀 Features

### Core Functionality
- **Multi-Modal Chat**: Support for both normal conversational AI and RAG mode for document-based queries
- **Tool Integration**: Extensible tool system with web search, calculations, and custom integrations
- **Conversation Management**: Create, rename, resume, and organize chat threads
- **User Authentication**: Secure JWT-based authentication with session management
- **Real-time Responses**: Streaming responses for better user experience

### Advanced Features
- **MCP (Model Context Protocol) Support**: Integration with external tools and services
- **LangSmith Integration**: Advanced tracing, debugging, and monitoring of AI conversations
- **Web Search**: Built-in DuckDuckGo search integration for real-time information
- **Session Persistence**: Redis-based session storage for fast conversation retrieval
- **Multi-User Support**: Individual user accounts with isolated chat histories

### AI & LLM Features
- **Multiple AI Providers**: Support for OpenAI, Google AI, and other LangChain-compatible models
- **LangGraph Integration**: Advanced conversation flow management and tool orchestration
- **Conversation Memory**: Persistent chat history with context awareness
- **Tool Calling**: Intelligent tool selection and execution during conversations

## 🏗️ Architecture

```
ChronoChat/
├── Backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/               # API endpoints
│   │   ├── core/              # Core configurations
│   │   ├── models/            # Database models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── services/          # Business logic
│   │   └── utils/             # Utilities and dependencies
│   ├── main.py                # FastAPI application entry point
│   └── docker-compose.yml     # Multi-service Docker setup
├── langgraph_backend.py       # LangGraph conversation engine
├── streamlit_frontend.py      # Streamlit web interface
└── pyproject.toml            # Python dependencies
```

## 🛠️ Technology Stack

### Backend
- **FastAPI**: High-performance Python web framework
- **SQLAlchemy**: ORM for database operations
- **PostgreSQL**: Primary database for user data and chat history
- **Redis**: Session storage and caching
- **Alembic**: Database migrations

### AI/ML Stack
- **LangChain**: LLM framework and integrations
- **LangGraph**: Conversation flow management
- **LangSmith**: AI observability and monitoring
- **OpenAI GPT**: Primary language model
- **Google AI**: Alternative AI provider

### Frontend
- **Streamlit**: Interactive web application framework
- **Modern UI Components**: Clean, responsive design

### Tools & Integrations
- **DuckDuckGo Search**: Web search capabilities
- **MCP Protocol**: External tool integrations
- **Custom Tools**: Extensible tool system

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL 13+
- Redis 6+
- Docker & Docker Compose (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ChronoChat
   ```

2. **Set up environment variables**
   ```bash
   # Root directory
   cp .env.example .env
   # Edit .env with your API keys
   
   # Backend directory
   cd Backend
   cp .env.example .env
   # Edit Backend/.env with database and Redis configurations
   ```

3. **Install dependencies**
   ```bash
   # Using uv (recommended)
   uv pip install -e .
   
   # Or using pip
   pip install -r Backend/requirements.txt
   ```

### Running the Application

#### Option 1: Docker Compose (Recommended)
```bash
cd Backend
docker-compose up -d
```

#### Option 2: Manual Setup
```bash
# Terminal 1: Start Backend
cd Backend
uvicorn main:app --reload --port 8000

# Terminal 2: Start Streamlit Frontend
streamlit run streamlit_frontend.py

# Terminal 3: LangGraph Backend (if needed)
python langgraph_backend.py
```

### Access Points
- **Streamlit Frontend**: http://localhost:8501
- **FastAPI Backend**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📖 Usage Guide

### Chat Modes

#### Normal Mode
- Standard conversational AI
- Direct model interactions
- Tool calling when needed
- Real-time web search integration

#### RAG Mode
- Document-based question answering
- Upload and query documents
- Context-aware responses
- Source citation

### Chat Management
- **New Chat**: Start fresh conversations
- **Rename Chats**: Organize conversations with custom titles
- **Resume Chat**: Continue previous conversations
- **Chat History**: Browse and search past conversations

### Tool Integration
- **Web Search**: Real-time information from DuckDuckGo
- **Calculations**: Built-in mathematical operations
- **Custom Tools**: Extensible plugin system
- **MCP Integration**: External service connections

## 🔧 Configuration

### Environment Variables

#### Root `.env`
```bash
# AI Provider Keys
OPENAI_API_KEY=your-openai-key
GOOGLE_API_KEY=your-google-key

# LangSmith (optional)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your-langsmith-key
```

#### Backend `.env`
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/chronochat

# Redis
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-super-secret-key
```

### AI Model Configuration
- Default: OpenAI GPT-3.5-turbo
- Configurable via environment variables
- Support for multiple providers

## 🔌 API Documentation

### Authentication Endpoints
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Token refresh
- `POST /api/auth/logout` - User logout

### Chat Endpoints
- `POST /api/chat/send` - Send message
- `GET /api/chat/threads` - List chat threads
- `GET /api/chat/threads/{id}` - Get chat history
- `PUT /api/chat/threads/{id}/title` - Rename chat
- `DELETE /api/chat/threads/{id}` - Delete chat

### User Management
- `GET /api/users/profile` - User profile
- `PUT /api/users/profile` - Update profile
- `POST /api/users/change-password` - Change password

## 🧪 Development

### Project Structure
```
Backend/
├── app/
│   ├── api/routes/           # API endpoints
│   │   ├── auth.py          # Authentication
│   │   ├── chat.py          # Chat management
│   │   └── users.py         # User management
│   ├── core/                # Core configurations
│   │   ├── config.py        # Settings
│   │   ├── database.py      # DB connection
│   │   ├── security.py      # JWT & passwords
│   │   └── redis.py         # Redis client
│   ├── models/              # SQLAlchemy models
│   │   ├── user.py          # User models
│   │   └── chat.py          # Chat models
│   ├── schemas/             # Pydantic schemas
│   │   ├── auth.py          # Auth schemas
│   │   └── chat.py          # Chat schemas
│   └── services/            # Business logic
│       ├── auth.py          # Auth service
│       └── chat.py          # Chat service
```

### Database Schema
- **Users**: User accounts and authentication
- **UserSessions**: Active user sessions
- **ChatThreads**: Conversation threads
- **ChatMessages**: Individual messages
- **ToolCalls**: Tool usage tracking

### Adding New Tools
1. Create tool function in `langgraph_backend.py`
2. Register with LangGraph agent
3. Add to tool registry
4. Update documentation

## 🔒 Security Features

- JWT access and refresh tokens
- Password hashing with bcrypt
- Session management with Redis
- CORS protection
- Rate limiting (configurable)
- SQL injection prevention
- Input validation and sanitization

## 📊 Monitoring & Observability

### LangSmith Integration
- Conversation tracing
- Performance monitoring
- Error tracking
- Usage analytics

### Health Checks
- Database connectivity
- Redis availability
- AI service status
- Application health endpoints

## 🚀 Deployment

### Docker Deployment
```bash
cd Backend
docker-compose up -d
```

### Production Considerations
- Use environment-specific configurations
- Set up SSL/HTTPS
- Configure proper logging
- Set up monitoring and alerting
- Use production-grade database
- Implement backup strategies

### Environment-Specific Configs
- Development: Hot reload, debug logging
- Staging: Similar to production, with test data
- Production: Optimized, secure, monitored

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

### Development Guidelines
- Follow PEP 8 for Python code
- Add type hints to all functions
- Write comprehensive tests
- Update documentation
- Use meaningful commit messages

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Common Issues
- **Database Connection**: Verify PostgreSQL is running
- **Redis Connection**: Check Redis server status
- **API Keys**: Ensure all required keys are set
- **Port Conflicts**: Check if ports 8000, 8501 are available

### Getting Help
- Check the [API documentation](http://localhost:8000/docs)
- Review the [troubleshooting guide](Backend/README.md)
- Open an issue on GitHub

## 🔄 Version History

- **v1.0.0**: Initial release with core chat functionality
- **Planned**: RAG mode, advanced tool integrations, mobile support

## 🎯 Roadmap

- [ ] RAG mode implementation
- [ ] Mobile-responsive design
- [ ] Voice input/output
- [ ] Advanced tool marketplace
- [ ] Multi-language support
- [ ] Enterprise features

---

**ChronoChat** - Intelligent conversations, powered by modern AI 🤖✨