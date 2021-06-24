#!/bin/bash
cd ~/code
mkdir logs
logparser -dir /code/logs -t 10 --delete_json_files & scrapyd