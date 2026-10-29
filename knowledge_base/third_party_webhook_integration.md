# Debugging Third-Party Webhook Signature Verification Failures

## Overview
External partner integrations fail because inbound webhook payloads are rejected due to cryptographic signature mismatch errors.

## Common Error Codes & Resolution

### Error: `WEBHOOK_ERR_INVALID_SIGNATURE`
* **Symptom:** Webhook endpoints return a 400 Bad Request with an invalid signature header error.
* **Root Cause:** The raw request body stream was modified or parsed as JSON before the HMAC SHA256 signature hash was computed.
* **Step-by-Step Resolution:**
  1. Verify that the incoming request header `X-Signature-Sha256` matches the computed HMAC hex digest.
  2. Ensure your web framework middleware reads the **raw binary request body** before json decoding.
  3. Check if the shared secret key was updated on the partner's management portal.