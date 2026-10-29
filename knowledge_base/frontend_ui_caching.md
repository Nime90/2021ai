# Resolving UI White Screens and Old Asset Caching

## Overview
Back-office users and clients often experience stale frontend states, layout breakage, or white-screen-of-death errors following minor deployment releases.

## Common Error Codes & Resolution

### Error: `UI_ERR_CHUNK_LOAD_FAILED`
* **Symptom:** Users report a blank white screen or a JavaScript toast saying `Loading chunk X failed` after a new version is pushed.
* **Root Cause:** The browser is trying to load old hashed JavaScript bundles from cache that no longer exist on the CDN server.
* **Step-by-Step Resolution:**
  1. Instruct the user to perform a hard refresh (`Ctrl + Shift + R` on Windows, `Cmd + Shift + R` on Mac) to bypass service worker caches.
  2. Verify Cloudflare/CDN cache purge status for `/static/js/*.js` assets.
  3. Ensure cache-control headers on index.html are explicitly set to `no-cache, no-store, must-revalidate`.