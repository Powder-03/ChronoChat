-- Initialize the database
CREATE DATABASE IF NOT EXISTS chronochat;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE chronochat TO chronochat;
