# Docker Container Health Checks and OOM Kills

## Overview
When deploying microservices or running local QA environments, container crashes and Out-Of-Memory (OOM) exceptions disrupt internal operations.

## Common Error Codes & Resolution

### Error: `DEVOPS_ERR_137_OOM_KILLED`
* **Symptom:** Support containers or worker nodes exit unexpectedly with exit code `137`.
* **Root Cause:** The container exceeded its assigned RAM limit in Docker/Kubernetes, triggering the Linux kernel's Out-Of-Memory killer.
* **Step-by-Step Resolution:**
  1. Check container exit history via Docker: `docker inspect <container_name> --format='{{.State.ExitCode}}'`
  2. Inspect system kernel logs for OOM events: `dmesg -T | grep -i oom`
  3. Increase the memory limit in `docker-compose.yml`:
```yaml
deploy:
  resources:
    limits:
      memory: 4G