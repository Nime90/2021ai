# Handling TLS/SSL Certificate Expiry and Handshake Errors

## Overview
Clients and internal tools face browser security warnings or API connection rejections due to expired certificates.

## Common Error Codes & Resolution

### Error: `SSL_ERR_CERT_DATE_INVALID`
* **Symptom:** API clients throw SSL verification errors and load balancers drop secure connections.
* **Root Cause:** The Let's Encrypt automated TLS renewal cron job failed, causing the domain certificate to expire.
* **Step-by-Step Resolution:**
  1. Check certificate expiration date via OpenSSL:
     `echo | openssl s_client -connect api.yourdomain.com:443 2>/dev/null | openssl x509 -noout -dates`
  2. Force manual certificate renewal on the Nginx/Certbot proxy:
     `sudo certbot renew --force-renewal`
  3. Reload Nginx configuration: `sudo systemctl reload nginx`