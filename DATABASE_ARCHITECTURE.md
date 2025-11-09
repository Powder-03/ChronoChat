# ChronoChat Database Architecture

## Overview

ChronoChat uses a hybrid database approach:
- **PostgreSQL**: User data, analytics, sessions, and structured data
- **MongoDB**: Conversations and messages (chat history)
- **Redis**: Caching and rate limiting

## Why This Architecture?

### PostgreSQL (Relational)
- **User Management**: User profiles with relationships to usage stats, preferences
- **Analytics**: API logs, session tracking with complex queries
- **ACID Compliance**: Critical user data requires transactions

### MongoDB (Document)
- **Conversations**: Flexible schema for chat messages
- **Scalability**: Better horizontal scaling for high-volume chat data
- **Performance**: Fast reads/writes for real-time chat
- **Flexibility**: Easy to add metadata to messages without schema changes

### Redis (Cache)
- **Session Storage**: Fast session lookups
- **Rate Limiting**: API throttling
- **Real-time Features**: WebSocket connection management (future)

## Database Schemas

### PostgreSQL Tables

#### users
```sql
- id: UUID (PK)
- clerk_user_id: String (Unique, Indexed)
- email: String
- username: String
- first_name: String
- last_name: String
- profile_image_url: String
- subscription_tier: String (free, pro, enterprise)
- is_active: Boolean
- created_at: DateTime
- updated_at: DateTime
- last_login_at: DateTime
- metadata: JSONB
```

#### user_usage_stats
```sql
- id: UUID (PK)
- clerk_user_id: String (Indexed)
- total_messages: Integer
- total_conversations: Integer
- total_tokens_used: Integer
- monthly_messages: Integer
- monthly_tokens: Integer
- month_year: String (e.g., "2025-11")
- created_at: DateTime
- updated_at: DateTime
```

#### user_sessions
```sql
- id: UUID (PK)
- clerk_user_id: String (Indexed)
- session_id: String (Unique, Indexed)
- ip_address: String
- user_agent: String
- device_type: String
- started_at: DateTime
- last_activity_at: DateTime
- ended_at: DateTime
- metadata: JSONB
```

#### api_logs
```sql
- id: UUID (PK)
- clerk_user_id: String (Indexed)
- endpoint: String (Indexed)
- method: String
- status_code: Integer
- response_time_ms: Float
- ip_address: String
- user_agent: String
- error_message: Text
- created_at: DateTime (Indexed)
```

#### user_preferences
```sql
- id: UUID (PK)
- clerk_user_id: String (Unique, Indexed)
- preferred_ai_provider: String (gemini, openai)
- preferred_model: String
- temperature: Float
- chat_theme: String (light, dark)
- language: String
- email_notifications: Boolean
- preferences: JSONB
- created_at: DateTime
- updated_at: DateTime
```

### MongoDB Collections

#### conversations
```javascript
{
  _id: ObjectId,
  conversation_id: String (UUID, Indexed),
  user_id: String (Clerk ID, Indexed),
  title: String,
  summary: String,
  created_at: DateTime (Indexed),
  updated_at: DateTime,
  message_count: Integer,
  total_tokens: Integer,
  metadata: Object,
  tags: [String],
  is_archived: Boolean
}
```

#### messages
```javascript
{
  _id: ObjectId,
  conversation_id: String (Indexed),
  role: String (user, assistant, system),
  content: String,
  created_at: DateTime (Indexed),
  model: String,
  provider: String,
  tokens: Integer,
  metadata: Object
}
```

## Indexes

### MongoDB Indexes
- `conversations.user_id` - Find user's conversations
- `conversations.created_at` - Sort by date
- `messages.conversation_id` - Get conversation messages
- `messages.created_at` - Sort messages by time

### PostgreSQL Indexes
- `users.clerk_user_id` - Fast user lookups
- `users.email` - Email searches
- `user_usage_stats.clerk_user_id` - Usage queries
- `user_sessions.clerk_user_id` - Session queries
- `user_sessions.session_id` - Session validation
- `api_logs.clerk_user_id` - User activity logs
- `api_logs.endpoint` - Endpoint analytics
- `api_logs.created_at` - Time-based queries

## Migrations

### PostgreSQL Migrations (Alembic)
```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### MongoDB Migrations
MongoDB is schema-less, but we maintain consistency through:
- Pydantic models for validation
- Application-level schema enforcement
- Index management on startup

## Backup Strategy

### PostgreSQL
```bash
# Backup
docker exec chronochat-postgres pg_dump -U chronochat chronochat > backup.sql

# Restore
docker exec -i chronochat-postgres psql -U chronochat chronochat < backup.sql
```

### MongoDB
```bash
# Backup
docker exec chronochat-mongodb mongodump --username=chronochat --password=chronochat --authenticationDatabase=admin --db=chronochat --out=/backup

# Restore
docker exec chronochat-mongodb mongorestore --username=chronochat --password=chronochat --authenticationDatabase=admin --db=chronochat /backup/chronochat
```

## Connection Pools

### PostgreSQL
- Pool size: 10
- Max overflow: 20
- Pre-ping: Enabled

### MongoDB
- Motor (async driver) handles connection pooling automatically
- Connections are lazy and created on demand

## Best Practices

1. **Use PostgreSQL for**:
   - User authentication data
   - Financial/billing data
   - Data requiring ACID transactions
   - Complex analytical queries
   - Structured relationships

2. **Use MongoDB for**:
   - Chat messages (high volume)
   - Flexible/evolving schemas
   - Nested/hierarchical data
   - Time-series data
   - Real-time features

3. **Use Redis for**:
   - Session storage
   - Rate limiting
   - Temporary cache
   - Real-time features (pub/sub)
