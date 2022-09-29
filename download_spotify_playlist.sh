#!/bin/bash

# ============================ USER INPUTS ===========================================
# Type here the playlist URI
URI="spotify:playlist:1cSukodzZOmPh6LtRGFmn9"
# ====================================================================================

source ~/.bash_profile

# Activate the conda environment
conda activate youtube

# Get the track information
echo "Getting Playlist Information..."
python emd/spotify_crawler.py -u=$URI

# Find the last json file created
NAME=$(find "Playlists" -name "*.json" -print0 | xargs -r -0 ls -1 -t | head -1)

# Find the Youtube URLs
echo
echo "Getting Youtube links..."
python emd/youtube_crawler/from_spotify_playlist.py -p=$NAME

# Find the last json file created
NAME=$(find "Queries" -name "*.json" -print0 | xargs -r -0 ls -1 -t | head -1)

# Download each track
echo
echo "Starting the download..."
python emd/mp3_downloader/download_queries.py -q=$NAME

# ====================================================================================

echo "Done!"