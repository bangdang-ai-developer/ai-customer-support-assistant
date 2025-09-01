-- PostgreSQL initialization script for BIWOCO AI Customer Support Assistant
-- This script sets up the database, user, and basic configuration

-- Create application user (if not using default postgres user)
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'biwoco_user') THEN

      CREATE ROLE biwoco_user LOGIN PASSWORD 'your-secure-password';
   END IF;
END
$do$;

-- Grant privileges to the application user
GRANT ALL PRIVILEGES ON DATABASE biwoco_chatbot_dev TO biwoco_user;
GRANT ALL PRIVILEGES ON DATABASE biwoco_chatbot TO biwoco_user;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For text search
CREATE EXTENSION IF NOT EXISTS "btree_gin"; -- For better indexing

-- Set up basic configuration
ALTER DATABASE biwoco_chatbot_dev SET timezone = 'UTC';
ALTER DATABASE biwoco_chatbot SET timezone = 'UTC';

-- Create a simple health check function
CREATE OR REPLACE FUNCTION health_check()
RETURNS TABLE(status text, timestamp timestamp with time zone) AS $$
BEGIN
    RETURN QUERY SELECT 'healthy'::text, now();
END;
$$ LANGUAGE plpgsql;