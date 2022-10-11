#!/bin/bash

source ~/.bash_profile

# Activate the conda environment
conda activate emd

# Get the track information
echo "Getting Chart Information..."
python emd/beatport/chart_scraper.py -u=$1

# Find the last json file created
chart_path=$(find "Charts" -name "*.json" -print0 | xargs -r -0 ls -1 -t | head -1)

# Find the Youtube URLs
echo
echo "Getting Youtube links..."
python emd/youtube/youtube_searcher.py -p=$chart_path

# Use the name of the chart to get the query path
query_path="$(basename $chart_path .json)-Queries.json"

# Download each track
echo
echo "Starting the download..."
python emd/youtube/download_queries.py -p=$query_path --clean

echo "Done!"