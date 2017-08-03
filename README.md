# infra_helpers
Repo for scripts/tools for DevOps things.

## backup_mysql_to_s3.sh
Script used to take GZIPed backup of database and upload it to S3.

Usage:

`./backup_mysql_to_s3.sh s3://example_bucket/folder/`

+ Add it to cron to automate DB backups.
+ Add lifecycle policies to target S3 bucket to control previous versions.
