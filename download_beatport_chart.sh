#!/bin/bash

# ============================ USER INPUTS ===========================================
# URL of the chart
URL="https://www.beatport.com/genre/techno-peak-time-driving/6/top-100"
NAME="Try2"
# ====================================================================================

source ~/.bash_profile

# Activate the conda environment
conda activate youtube

# Get the track information
echo "Getting Chart Information..."
python emd/analyze_beatport.py -u=$URL -o="Charts/$NAME" --save-figure

# Locate the chart analysis file and create the chart_file name
chart_file="$(find "Charts/$NAME" -type f -name "*.json")"
name=$(basename $chart_file .json)

# Find the Youtube URLs
echo
echo "Getting Youtube links..."
python emd/youtube_crawler/from_beatport_chart.py -c=$chart_file

# Download each track
echo
echo "Starting the download..."
python emd/mp3_downloader/download_queries.py -q="Queries/$name-Queries.json"

# ====================================================================================
echo "Done!"
