#!/bin/bash

# Initialize things
mysql_password=""
target_bucket=$1
timestamp=`date +"%s_%d-%B-%Y_%A@%H%M"`

if [ -z "$1" ]; then
    echo "Argument containing target S3 bucket path must be passed. Exiting."
    exit 0
fi

command -v aws >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "AWS CLI not installed. Exiting."
    exit 0
fi

echo `date +"%d-%B-%Y@%H:%M:%S"`" - Starting backups."

# List all the databases
databases=`mysql -uroot -e "SHOW DATABASES;" | tr -d "| " | grep -v "\(Database\|information_schema\|performance_schema\|mysql\|test\)"`

# Loop the databases
for db in $databases; do

  echo `date +"%d-%B-%Y@%H:%M:%S"`" - Processing database $db."

  filename="${timestamp}_$db.sql.gz"
  tmp=/tmp/$filename

  # Dump
  echo `date +"%d-%B-%Y@%H:%M:%S"`" - Dumping $db to $tmp."
  mysqldump -uroot --force --opt --databases $db | gzip -c > $tmp
  size=`stat -c "%s" $tmp`
  echo `date +"%d-%B-%Y@%H:%M:%S"`" - File size of $tmp is $size bytes."

  # Upload
  echo `date +"%d-%B-%Y@%H:%M:%S"`" - Uploading $tmp to $target_bucket$filename."
  aws s3 cp $tmp $target_bucket$filename

  # Cleanup
  echo `date +"%d-%B-%Y@%H:%M:%S"`" - Cleaning up $tmp."
  rm $tmp

done;

# All done
echo `date +"%d-%B-%Y@%H:%M:%S"`" - All done."