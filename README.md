# Infrastructure Helpers
Those of us who spend our days managing cloud infrastructure have to work with a variety of tools, but a lot of what we do is exactly the same everywhere, and shouldn't require us to write things from scratch.

This repository contains helpers scripts that might be useful for infrastructure automation. I'm hoping open-sourcing these will encourage re-use and save us all a lot of time and heartache. If you have a useful script that you think can be used by the larger community, please issue a pull request.

- All scripts should end in the extension indicatiing their programming lanuage: `.sh` for `bash`, `.py` for `Pythong`, etc.
- Please add **lots of comments** in your code so that users can know what the scripts for without coming back to this readme.

## General Scripts (`general/`)

## backoff_strategies.py
Python code demonstrating backoff strategies. Useful for retrying remote endpoints after a certain delay if they are temporarily down.

Strategies included:

- No backoff: If things fail, retry immediately.
- Constant backoff: If things fail, retry after a fixed amount of delay.
- Linear backoff: If things fail, retry with linearly increasing delays.
- Fibonacci backoff: If things fail, retry with delays increasing by fibonacci numbers.
- Exponential backoff: If things fail, retry with exponentially increasing delays.
- Quadratic backoff: If things fail, retry with polynomially increasing delays.
- Polynomial backoff: If things fail, retry with polynomially increasing delays.

Usage:

`python3 backoff_strategies.py`

Sample Output:

```bash
Starting tests with maximum 3 retries.
> No Backoff > Retry number: 0
> No Backoff > Retry number: 1
> No Backoff > Retry number: 2
> Constant Backoff > Retry number: 0, sleeping for 1 seconds.
> Constant Backoff > Retry number: 1, sleeping for 1 seconds.
> Constant Backoff > Retry number: 2, sleeping for 1 seconds.
> Constant Backoff > Total delay: 3 seconds.
> Linear Backoff > Retry number: 0, sleeping for 0 seconds.
> Linear Backoff > Retry number: 1, sleeping for 1 seconds.
> Linear Backoff > Retry number: 2, sleeping for 2 seconds.
> Linear Backoff > Total delay: 3 seconds.
> Fibonacci Backoff > Retry number: 0, sleeping for 0 seconds.
> Fibonacci Backoff > Retry number: 1, sleeping for 1 seconds.
> Fibonacci Backoff > Retry number: 2, sleeping for 1 seconds.
> Fibonacci Backoff > Total delay: 2 seconds.
> Quadratic Backoff > Retry number: 0, sleeping for 0 seconds.
> Quadratic Backoff > Retry number: 1, sleeping for 1 seconds.
> Quadratic Backoff > Retry number: 2, sleeping for 4 seconds.
> Quadratic Backoff > Total delay: 5 seconds.
> Exponential Backoff > Retry number: 0, sleeping for 1 seconds.
> Exponential Backoff > Retry number: 1, sleeping for 2 seconds.
> Exponential Backoff > Retry number: 2, sleeping for 4 seconds.
> Exponential Backoff > Total delay: 7 seconds.
> Polynomial Backoff > Retry number: 0, sleeping for 0 seconds.
> Polynomial Backoff > Retry number: 1, sleeping for 1 seconds.
> Polynomial Backoff > Retry number: 2, sleeping for 8 seconds.
> Polynomial Backoff > Total delay: 9 seconds.
```

## post_to_slack.py
Python script to post messages to Slack channel using Slack's incoming webhooks.

- Configure `wekbook_url` in file to point to your Slack's incoming webhooks URL.
- Configure `data` in file to update the message text that is posted, the user that will post the message, and the user's image icon.

Usage:

`python3 post_to_slack.py`


## AWS Scripts (`aws/`)

### aws_elb_check_elb.py
This script will find all the instances behind an AWS ELB and get the HTTP response status code for a particular path. Useful to find out if the ELB is correctly forwarding requests to the backend instances.

Usage:

`python3 aws_elb_check_elb.py --elb_name http://elb.region.elb.amazon.aws.com --path health_check_path`

### aws_route53_register_deregister_instance.py
This script will add the public IP of the instance it is running on to a Route 53 DNS record you specify.Uses weighted routing to divide IPs into buckets.

Usage:

`python3 aws_route53_register_deregister_instance.py --record_name DOMAIN_NAME --record_type RECORD_TYPE --record_ttl RECORD_TTL --hosted_zone_id HOSTED_ZONE_ID --action add`

For example:

`python3 aws_route53_register_deregister_instance.py --record_name record.example.com --record_type A --record_ttl 60 --hosted_zone_id HOSTED_ZONE_ID --action add`

For removing entries, use `--action remove`.


## InfluxDB Scripts (`influxdb/`)

## backup_influxdb_to_s3.sh
Backup all InfluxDB databases to S3.

Usage:

`./backup_influxdb_to_s3.sh s3://example_bucket/folder/`


## MySQL Scripts (`mysql/`)

## backup_mysql_to_s3.sh
Take `mysqldump`s of all databases on the local system, `gzip` them all, and upload them to AWS S3.

Usage:

`./backup_mysql_to_s3.sh s3://example_bucket/folder/`

- Add this script to a cron to automate DB backups.
- Add lifecycle policies to the S3 S3 bucket to control how many last backups to keep.

## Bitbucket scripts (`bitbucket/`)

## report_repos_pipelines.py
Connect to Bitbucket via OAuth and download a list of all repos and pipelines for that account. Script creates `repos.csv` and `pipelines.csv` as artifacts.

Requirements:
- `requests`
- `requests-oauthlib`

Configuration:
- `c.client_id`: Bitbucket OAuth consumer client_id.
- `c.client_secret`: Bitbucket OAuth consumer client_secret.
- `account_id`: Bitbucket account UUID.

Usage:

`python report_repos_pipelines.py`