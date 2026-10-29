# Troubleshooting OAuth2 and SSO Authentication Errors

## Overview
Internal and enterprise customer support teams frequently encounter authentication issues tied to token expiration, misconfigured identity providers (IdP), or OAuth2 scope mismatches.

## Common Error Codes & Resolution

### Error: `AUTH_ERR_401_EXPIRED_TOKEN`
* **Symptom:** Users get logged out unexpectedly or API calls return a 401 Unauthorized status code.
* **Root Cause:** The JSON Web Token (JWT) has exceeded its standard 60-minute lifetime and the refresh token mechanism failed.
* **Step-by-Step Resolution:**
  1. Check the client system clock synchronization (NTP drift > 5 minutes invalidates tokens).
  2. Verify that the `REFRESH_TOKEN_ENABLED` environment variable is set to `true` in the config service.
  3. Clear browser local storage/session storage and force a re-authentication flow against the IdP.
  4. If the issue persists, inspect the Keycloak/Okta logs for client secret expiration.

### Error: `AUTH_ERR_403_SCOPE_MISMATCH`
* **Symptom:** Users can log in, but certain back-office modules throw a "Forbidden" exception.
* **Root Cause:** The user role lacks the required scopes (`read:reports`, `execute:backoffice`).
* **Step-by-Step Resolution:**
  1. Navigate to the Admin Panel > User Management > Roles.
  2. Confirm the user is mapped to the correct LDAP/Active Directory group.
  3. Force-sync permissions using the CLI tool: `python manage.py sync_permissions --user=<email>`