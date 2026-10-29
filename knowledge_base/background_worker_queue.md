# Celery and Redis Background Worker Queue Stalls

## Overview
Async tasks like report generation, bulk data syncs, and email batching get stuck indefinitely in the processing queue.

## Common Error Codes & Resolution

### Error: `WORKER_ERR_TASK_TIMEOUT`
* **Symptom:** Background jobs freeze and eventually throw a `SoftTimeLimitExceeded` exception.
* **Root Cause:** A heavy SQL query or external API call inside a Celery task exceeded the default execution time limit of 300 seconds.
* **Step-by-Step Resolution:**
  1. Check active worker status and queue length via Flower or CLI:
     `celery -A core inspect active`
  2. Restart hanging workers safely:
     `celery -A core worker --purge`
  3. Increase the soft time limit configuration in `celery.py`:
     `task_soft_time_limit = 600`