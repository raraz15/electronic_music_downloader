# electronic_music_downloader

A repository for downloading high quality electronic music from YouTube with Spotify and Beatport crawling capacities.

### TODO: 
    Update the environment file
    Path of the dummy client info        

1) Create the Environment:

    conda create --name myenv --file requirements.txt

2) You will need the ffmpeg for youtube-dl.

    For MacOS: 

        brew install ffmpeg

    For Linux:

        sudo apt-get install ffmpeg

3) Activate the environment

    conda activate myenv

4) How to use

    python mp3_downloader.py -l="youtube_link"