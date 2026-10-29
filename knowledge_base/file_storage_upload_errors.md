# Resolving Cloud Storage and Multipart Upload Failures

## Overview
Users uploading large attachments, profile avatars, or report exports encounter bucket permission errors or size threshold blocks.

## Common Error Codes & Resolution

### Error: `STORAGE_ERR_403_S3_ACCESS_DENIED`
* **Symptom:** File uploads fail instantly with an S3 Forbidden exception.
* **Root Cause:** The IAM role assigned to the backend service lacks `s3:PutObject` and `s3:PutObjectAcl` permissions on the target bucket.
* **Step-by-Step Resolution:**
  1. Inspect the AWS IAM policy attached to the running instance profile or ECS task role.
  2. Verify that the bucket name in `STORAGE_BUCKET_NAME` matches the environment variable exactly.
  3. Ensure the bucket CORS configuration allows PUT requests from the application domain.