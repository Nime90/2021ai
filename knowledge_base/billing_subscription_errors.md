# Handling Subscription Failures and Webhook Sync Errors

## Overview
Customer support frequently handles payment gateway failures, stripe webhook disconnections, and subscription license provisioning blocks.

## Common Error Codes & Resolution

### Error: `BILLING_ERR_902_STRIPE_WEBHOOK_FAILED`
* **Symptom:** Customers upgrade their plan on the pricing page, but their account remains on the "Free" tier.
* **Root Cause:** The Stripe webhook endpoint returned a 500 error or signature verification failed due to rotated API keys.
* **Step-by-Step Resolution:**
  1. Go to Stripe Dashboard > Developers > Webhooks and check the recent delivery logs for event `checkout.session.completed`.
  2. Verify that the `STRIPE_WEBHOOK_SECRET` environment variable matches the active signing secret on the server.
  3. Manually trigger a license sync by running the backend admin command:
     `python manage.py resync_license --customer-email=<email>`