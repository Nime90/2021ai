# Resolving Audit Log and Report Export Memory Overflows

## Overview
Compliance officers and back-office admins attempting to download multi-year audit logs experience browser crashes or 504 gateway spikes.

## Common Error Codes & Resolution

### Error: `EXPORT_ERR_MEMORY_OVERFLOW`
* **Symptom:** Exporting CSV or PDF audit logs causes the worker node to consume 100% RAM and crash.
* **Root Cause:** The backend code is attempting to load millions of audit rows into memory at once instead of using database cursor pagination.
* **Step-by-Step Resolution:**
  1. Check system RAM usage during exports using `htop`.
  2. Instruct users to narrow down the date range filter to chunks of 30 days or less.
  3. Ensure pagination chunk size is set to 5,000 records in `exports/tasks.py`.