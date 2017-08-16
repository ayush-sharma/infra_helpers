# infra_helpers
Repo for scripts/tools for DevOps things.

## aws/aws_route53_register_deregister_instance.py
Script used to add or remove instance public IP to Route 53. Uses weighted routing to divide IPs into buckets.

Usage:

`python3 aws_route53_register_deregister_instance.py --record_name DOMAIN_NAME --record_type RECORD_TYPE --record_ttl RECORD_TTL --hosted_zone_id HOSTED_ZONE_ID --action add`

For example:

`python3 aws_route53_register_deregister_instance.py --record_name record.example.com --record_type A --record_ttl 60 --hosted_zone_id HOSTED_ZONE_ID --action add`

For removing entries, use `--action remove`.

## general/backoff_strategies.py
Some code demonstrating different backoff strategies for retrying after transient failures.

## mysql/backup_mysql_to_s3.sh
Script used to take GZIPed backup of database and upload it to S3.

Usage:

`./backup_mysql_to_s3.sh s3://example_bucket/folder/`

+ Add it to cron to automate DB backups.
+ Add lifecycle policies to target S3 bucket to control previous versions.

