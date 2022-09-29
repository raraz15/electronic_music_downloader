#!/bin/bash

# ============================ USER INPUTS ===========================================
# URL of the chart
URL="https://www.beatport.com/genre/tech-house/11/top-100"
# ====================================================================================

source ~/.bash_profile

# Activate the conda environment
conda activate youtube

# Get the track information
echo "Getting Chart Information..."
python emd/analyze_beatport.py -u=$URL --save-figure

# Find the last json file created
chart_path=$(find "Charts" -name "*.json" -print0 | xargs -r -0 ls -1 -t | head -1)

# Find the Youtube URLs
echo
echo "Getting Youtube links..."
python emd/youtube_crawler_from_beatport_chart.py -p=$chart_path

# Use the name of the chart to get the query path
query_path="$(basename $chart_path .json)-Queries.json"
#query_path="$query_path"

# Download each track
echo
echo "Starting the download..."
python emd/download_queries.py -p=$query_path

# ====================================================================================
echo "Done!"
