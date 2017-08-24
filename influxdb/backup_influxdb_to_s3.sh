#!/bin/bash

# Initialize things
target_bucket=$1
timestamp=`date +"%s_%d-%B-%Y_%A@%H%M"`
backup_tmp="/tmp/"`cat /dev/random | tr -dc "[:alpha:]" | head -c 8`
backup_tar_file="influxdb_backup_$timestamp.tar.gz"
backup_tar_path="/tmp/"

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

# Backup Metastore
rm -rf $backup_tmp
mkdir -p $backup_tmp
influxd backup $backup_tmp/metastore

# List all the databases
databases=` influx -execute 'show databases' | sed -n -e '/----/,$p' | grep -v -e '----' -e '_internal'`

# Loop the databases
for db in $databases; do

  echo `date +"%d-%B-%Y@%H:%M:%S"`" - Backing up database $db to $backup_tmp/$db."

  # Dump
  influxd backup -database $db $backup_tmp/$db

done;

# Create archive
echo `date +"%d-%B-%Y@%H:%M:%S"`" - Creating archive /tmp/influxdb_backup_$timestamp."
cd $backup_tmp
tar cvzf $backup_tar_path$backup_tar_file .

# Upload
echo `date +"%d-%B-%Y@%H:%M:%S"`" - Uploading $backup_tar_path$backup_tar_file to $target_bucket/$backup_tar_file."
aws s3 cp $backup_tar_path$backup_tar_file $target_bucket/$backup_tar_file

# Cleanup
echo `date +"%d-%B-%Y@%H:%M:%S"`" - Cleaning up."
#rm $backup_tar_path$backup_tar_file
rm -rf $backup_tmp

# All done
echo `date +"%d-%B-%Y@%H:%M:%S"`" - All done."