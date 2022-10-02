# electronic_music_downloader

A repository for downloading electronic music from YouTube with Spotify and Beatport crawling capacities. It could be used for other genres of music but our query algorithm is designed for electronic music traditions.

## TODO: 
- [ ] Update the environment file
- [ ] Path of the dummy client info
- [ ] Spotify Client, URI Information doc 
- [ ] Remove stuff like (Visualizer) from the downloaded file
- [ ] Beatport dict chart info and tracks
- [ ] Download the LOFI part from beatport

## Installation

### 1) Create the Environment:

    `conda create --name myenv --file environment.yml`

### 2) You will need the ffmpeg for youtube-dl.

    For MacOS: 

        `brew install ffmpeg`

    For Linux:

        `sudo apt-get install ffmpeg`
        

### 3) Make the bash files executable

    Using the terminal in the current directory:

    `chmod u+x spotify_playlist_download.sh`
    `chmod u+x beatport_chart_download.sh`


### 4) Activate the environment

    `conda activate myenv`

### 5) Get Spotify Client Information

    Put CLIENT_ID,CLIENT_SECRET these information in spotify_client_info.json
    

## Usage

    After completing the installation, you can use the pipeliness easily or use the python scripts individually.

### A) Pipelines  

#### Get metadata and Download mp3 files from a Spotify Playlist

##### 1) Get the URI of the Spotify Playlist

    Replace the URI in `spotify_playlist_download.sh` where it is indicated.

##### 2) Run the bash script

    From the terminal,

    `./spotify_playlist_download.sh`

#### Get metadata, Analyze and Download mp3 files from a Beatport Top100 Chart

##### 1) Get the URL of the Beatport Chart

    Replace the URL in `beatport_chart_download.sh` where it is indicated.
    
##### 2) Run the bash script

    From the terminal,

    `./beatport_chart_download.sh`    
    

### B) Single task python scripts

