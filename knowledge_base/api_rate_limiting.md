# Managing API Rate Limits and Throttling

## Overview
Enterprise clients integrating via webhooks or direct REST APIs frequently hit rate limits, triggering support inquiries about data ingestion failures.

## Common Error Codes & Resolution

### Error: `API_ERR_429_TOO_MANY_REQUESTS`
* **Symptom:** Client applications receive a `429 Too Many Requests` header response, halting automated syncs.
* **Root Cause:** The client exceeded the default threshold of 1,000 requests per minute per API key.
* **Step-by-Step Resolution:**
  1. Check the client's current usage metrics in the Redis cache tracker:
     `redis-cli GET rate_limit:<client_api_key>`
  2. If the client is a trusted enterprise partner requiring a temporary exemption, update their tier in the Kong API Gateway dashboard.
  3. Advise the customer support team to instruct the client to implement **exponential backoff retry logic** in their integration scripts.
Why this dataset works brilliantly for your interview: