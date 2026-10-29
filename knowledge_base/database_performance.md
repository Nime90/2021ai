# Database Connection Pooling & Query Timeout Runbook

## Overview
High-volume software environments often hit database connection bottlenecks, resulting in gateway timeouts (HTTP 504) and sluggish support ticket resolutions.

## Common Error Codes & Resolution

### Error: `DB_ERR_504_CONNECTION_TIMEOUT`
* **Symptom:** API requests hang for 30 seconds and then fail with a Gateway Timeout.
* **Root Cause:** The connection pool has exhausted its maximum limit (`max_overflow` reached) due to unclosed database cursors in microservices.
* **Step-by-Step Resolution:**
  1. Check current active database connections via SQL: 
     `SELECT count(*) FROM pg_stat_activity WHERE state = 'active';`
  2. If connections are maxed out, restart the connection pool proxy (PgBouncer):
     `sudo systemctl restart pgbouncer`
  3. Increase the pool size temporarily in `config/production.yaml`:
```yaml
database:
  pool_size: 50
  max_overflow: 10
  timeout: 30