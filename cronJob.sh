#!/bin/bash -f

echo "*/10 * * * * cd /usr/bin/python3 ./winner.py" >> cronjob
crontab cronjob
rm cronjob