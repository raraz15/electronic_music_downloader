# electronic_music_downloader

A repository for downloading electronic music from YouTube with Spotify and Beatport crawling capacities. It could be used for other genres of music but our query algorithm is designed for electronic music traditions.

## TODO: 
- [ ] Path of the dummy client info (before making public)
- [ ] Edit id3tag (update environment)

## Installation

### 1) Create the Environment:

    conda create --name emd --file environment.yml

### 2) You will need the ffmpeg for youtube-dl.

    For MacOS: 

        brew install ffmpeg

    For Linux:

        sudo apt-get install ffmpeg

### 3) Make the bash files executable

    Using the terminal in the current directory:

    chmod u+x spotify_playlist_download.sh
    chmod u+x beatport_chart_download.sh

### 4) Activate the environment

    conda activate emd

### 5) Get Spotify Client Information (optional)
    This part is only for using the spotify functionalities of the repository.

    To get information from your spotify playlists, you will need the CLIENT_ID,CLIENT_SECRET keys of the user (you). You can get these information following the steps in: https://developer.spotify.com/documentation/general/guides/authorization/app-settings/

    When you have these information, paste them in spotify_client_info.json


## Usage

    After completing the installation, you can use the pipeliness or use the python scripts individually.

### A) Pipelines

#### Get metadata, Analyze and Download mp3 files from a Beatport Top100 Chart

    From the terminal,

        ./beatport_chart_download.sh "URL of the Top100 Chart"

#### Get metadata and Download mp3 files from a Spotify Playlist

    To get the URI, open Spotify App from your computer, go to the playlist, click on the *more options* key (three dots), come to *share* while holding the **option key** on your keyboard. 

    The *Copy playlist link* button will change to *Copy Spotify URI*.

    From the terminal,

        ./spotify_playlist_download.sh "URI you just copied"


### B) Single task python scripts

