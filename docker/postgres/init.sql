-- PostgreSQL initialization script for Computer Vision MLOps

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Create additional schemas if needed
CREATE SCHEMA IF NOT EXISTS mlflow;
CREATE SCHEMA IF NOT EXISTS monitoring;

-- Create monitoring user for metrics collection
CREATE USER monitoring_user WITH ENCRYPTED PASSWORD 'monitoring_pass';
GRANT CONNECT ON DATABASE computer_vision_db TO monitoring_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO monitoring_user;
GRANT SELECT ON ALL TABLES IN SCHEMA information_schema TO monitoring_user;
GRANT SELECT ON ALL TABLES IN SCHEMA pg_catalog TO monitoring_user;

-- Performance tuning for ML workloads
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;

-- Reload configuration
SELECT pg_reload_conf();