#!/bin/bash

source ~/.bash_profile

# Activate the conda environment
conda activate emd

# Get the track information
echo "Getting Playlist Information..."
python emd/spotify/playlist_scraper.py -u=$1

# Find the last json file created
playlist_path=$(find "Playlists" -name "*.json" -print0 | xargs -r -0 ls -1 -t | head -1)

# Find the Youtube URLs
echo
echo "Getting Youtube links..."
python emd/youtube/youtube_searcher.py -p=$playlist_path

# Find the last json file created
query_path=$(find "Queries" -name "*.json" -print0 | xargs -r -0 ls -1 -t | head -1)

# Download each track
echo
echo "Starting the download..."
python emd/youtube/download_queries.py -p=$query_path --clean

echo "Done!"