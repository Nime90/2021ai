# Troubleshooting SMTP and Notification Delivery Failures

## Overview
Internal systems and customers experience missing email alerts, password reset delivery blocks, and SendGrid/SMTP relay rejections.

## Common Error Codes & Resolution

### Error: `EMAIL_ERR_535_SMTP_AUTHENTICATION`
* **Symptom:** System fails to send notification emails, logging an authentication credentials error.
* **Root Cause:** The SMTP password or API user key has been rotated or expired in the mail relay service.
* **Step-by-Step Resolution:**
  1. Verify the `SMTP_USER` and `SMTP_PASSWORD` environment variables in the notification service config.
  2. Check SendGrid or AWS SES dashboard logs for account suspension or IP block flags.
  3. Test connectivity directly from the server CLI: 
     `telnet smtp.sendgrid.net 587`