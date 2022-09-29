#!/bin/bash

# ============================ USER INPUTS ===========================================
# Type here the playlist URI
URI="spotify:playlist:1cSukodzZOmPh6LtRGFmn9"
# TODO: get playlist name from the API
NAME="Yo!"
# ====================================================================================

source ~/.bash_profile

# Activate the conda environment
conda activate youtube

# Get the track information
echo "Getting Playlist Information..."
python emd/spotify_crawler.py -u=$URI -n=$NAME

# Find the Youtube URLs
echo
echo "Getting Youtube links..."
python emd/youtube_crawler/from_spotify_playlist.py -p="Playlists/$NAME.json"

# Download each track
echo
echo "Starting the download..."
python emd/mp3_downloader/download_queries.py -q="$NAME-SpotifyQueries.json"

# ====================================================================================

echo "Done!"