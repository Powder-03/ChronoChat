# ChronoChat Backend Docker Setup

This directory contains the Docker configuration for the ChronoChat FastAPI backend.

## Quick Start

### Development Environment

1. **Copy environment file:**
   ```bash
   cp env.example .env
   ```

2. **Update .env file with your API keys** (optional for basic functionality)

3. **Start development environment:**
   ```bash
   docker-compose -f docker-compose.dev.yml up --build
   ```

4. **Access the application:**
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Production Environment

1. **Copy and configure environment:**
   ```bash
   cp env.example .env
   # Edit .env with production values
   ```

2. **Start production environment:**
   ```bash
   docker-compose up -d --build
   ```

3. **Access through Nginx:**
   - API: http://localhost/api/
   - Documentation: http://localhost/docs

## Services

### Backend (FastAPI)
- **Port:** 8000
- **Health Check:** http://localhost:8000/
- **Features:** Hot reload in development

### PostgreSQL Database
- **Port:** 5432
- **Database:** chronochat
- **User:** chronochat
- **Password:** chronochat (change in production)

### Redis Cache
- **Port:** 6379
- **Password:** chronochat (change in production)

### Nginx (Production only)
- **Port:** 80, 443
- **Features:** Rate limiting, security headers, load balancing

## API Endpoints

Based on your current backend structure, the following endpoints are available:

### Authentication (`/api/auth/`)
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Refresh tokens
- `POST /api/auth/logout` - User logout

### Chat (`/api/chat/`)
- `POST /api/chat/send` - Send chat message
- `GET /api/chat/threads` - Get user chat threads
- `GET /api/chat/history/{thread_id}` - Get chat history
- `DELETE /api/chat/thread/{thread_id}` - Delete chat thread

### Users (`/api/users/`)
- `GET /api/users/profile` - Get user profile
- `PUT /api/users/profile` - Update user profile
- `POST /api/users/change-password` - Change password
- `DELETE /api/users/account` - Delete user account

## Commands

### Development
```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up

# View logs
docker-compose -f docker-compose.dev.yml logs -f backend

# Stop services
docker-compose -f docker-compose.dev.yml down
```

### Production
```bash
# Start production environment
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down

# Remove volumes (WARNING: This will delete all data)
docker-compose down -v
```

### Database Management
```bash
# Connect to PostgreSQL
docker exec -it chronochat-postgres psql -U chronochat -d chronochat

# Connect to Redis
docker exec -it chronochat-redis redis-cli -a chronochat
```

## Environment Variables

Key environment variables to configure:

- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `SECRET_KEY` - JWT secret key (MUST change in production)
- `GOOGLE_API_KEY` - Google AI API key (optional)
- `OPENAI_API_KEY` - OpenAI API key (optional)
- `DEBUG` - Enable debug mode (false in production)

## Security Notes

1. **Change default passwords** in production
2. **Use strong SECRET_KEY** for JWT tokens
3. **Configure CORS_ORIGINS** properly
4. **Use HTTPS** in production (configure SSL certificates)
5. **Set up proper firewall rules**

## Troubleshooting

### Common Issues

1. **Port conflicts:** Make sure ports 5432, 6379, 8000 are available
2. **Permission errors:** Check Docker daemon permissions
3. **Database connection:** Verify PostgreSQL is running and accessible
4. **Redis connection:** Check Redis password and connectivity

### Useful Commands

```bash
# Check container status
docker-compose ps

# View container logs
docker-compose logs [service_name]

# Restart specific service
docker-compose restart [service_name]

# Rebuild containers
docker-compose up --build
```
