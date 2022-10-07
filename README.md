# electronic_music_downloader

A repository for obtaining metadata, downloading electronic music mp3s and editing ID3tags collected in Beatport and Traxsource Top100 charts and Spotify Playlists. It can make a Youtube search and download medium quality mp3 files (128kbps, 16bit) of these tracks. It can also crawl Beatport and Traxsource and plot informative analysis figures. Moreover, it can download the LoFi Preview mp3 files of the Beatport tracks.

## Table of Contents
* [Installation](#installation)
### List of Functions:
* [Get metadata from a Spotify Playlist](#spotify-playlist-scraper)
* [Get metadata from a Beatport Top100 Chart](#beatport-top100-chart-scraper)
* [Get metadata from a Traxsource Top100 Chart](#traxsource-top100-chart-scraper)
* [Analyze and plot distributions of a Top100 Chart](#chart-analysis)
* [Download LoFi Beatport Preview mp3 files of a Top100 Chart](#beatport-top100-chart-scraper)
* [Crawl Beatport to get metadata and Preview mp3 files of all Top100 Charts (genre-by-genre)](#beatport-genre-crawler)
* [Crawl Traxsource to get metadata of all Top100 Charts  (genre-by-genre) or curated lists](#traxsource-genre-crawler)
* [Make a Youtube search to find tracks uploaded to Youtube by the Artist or Label](#youtube-searcher)
* [Download mp3 files only if original sampling rate>44.1kHz with preferably 128kbps at 16 bits](#youtube-mp3-downloader)
### Pipelines
* [Get metadata and download the mp3 files of tracks of a Spotify Playlist with a pipeline](#get-metadata-of-a-spotify-playlist-and-download-mp3-files-from-youtube)
* [Get metadata and download the mp3 files of tracks of a Beatport Top100 Chart with a pipeline](#get-metadata-of-a-beatport-or-traxsource-top100-chart-and-download-mp3-files-from-youtube)
* [Get metadata and download the mp3 files of tracks of a Traxsource Top100 Chart with a pipeline](#get-metadata-of-a-beatport-or-traxsource-top100-chart-and-download-mp3-files-from-youtube)
### TODO:
- [ ] URL with _ or not?
- [ ] Put beatport url of each track
- [ ] TraxSource download Preview mp3
- [ ] Discogs scrape (Later)
- [ ] Id3tag: Mix type, remixers, artwork (Later)

## Installation

### 1) Create the Environment:
```bash
conda create --name emd --file environment.yml
```
`Note:` if you change the *emd* name, you should change the line 6 at the bash scripts accordingly.

### 2) You will need the ffmpeg for youtube-dl

For MacOS: 
```bash
brew install ffmpeg
```
For Linux:
```bash
sudo apt-get install ffmpeg
```
### 3) Make the bash scripts executable

Using the terminal in the current directory:
```bash
chmod u+x spotify_playlist_download.sh
chmod u+x beatport_chart_download.sh
chmod u+x traxsource_chart_download.sh
```
### 4) Activate the environment
```bash
conda activate emd
```
### 5) Get Spotify Client Information (Optional)

This part is only for using the Spotify functionalities of the repository.

To get information from your Spotify playlists, you will need the `CLIENT_ID,CLIENT_SECRET` keys of the user. You can get these information following the steps in: https://developer.Spotify.com/documentation/general/guides/authorization/app-settings/

When you have these information, paste them in `spotify_client_info.json`

## Pipelines

### Get metadata of a Beatport  or Traxsource Top100 Chart and Download mp3 files from Youtube
This pipeline does 3 things in series.
1. Gets the information of the tracks in a Beatport/Traxsource Top100 Chart
2. Makes Youtube searches for finding these tracks.
3. Only downloads the tracks if they satisfy certaion criteria.

```bash
./beatport_chart_download.sh <Top100_Chart_URL>
```
```bash
./traxsource_chart_download.sh <Top100_Chart_URL>
```

### Get metadata of a Spotify Playlist and Download mp3 files from Youtube
This pipeline does 3 things in series.
1. Gets the information of the tracks in a Spotify Playlist *you have created*
2. Makes Youtube searches for finding these tracks.
3. Only downloads the tracks if they satisfy certaion criteria.

To use this functionality you should:
1. Follow Installation [Part 5](#5-get-spotify-client-information-optional).
2. Get the playlist URI:<br>
Open Spotify App from your computer, go to the playlist, click on the *more options* key (three dots), come to *share* while holding the **option key** on your keyboard. The *Copy playlist link* button will change to *Copy Spotify URI*.

```bash
./spotify_playlist_download.sh <Spotify_playlist_URI>
```

## Single Task Python Scripts
Each of the scripts have a default directory where the outputs will be written. However, you can choose your own output directory with providing `-o` option.

### Beatport Top100 Chart Scraper
```bash
python emd/beatport/chart_scraper.py -u=<URL> --analyze --save-figure --preview
```
`--analyze`: Will perform Key, BPM, Label, Artist analysis<br>
`--save-figure`: Will save these figures<br>
`--preview`: Will download the LoFi Preview mp3 of the tracks<br>
Example of a track metadata:
```json
{
    "Title": "Yeah The Girls",
    "Mix": "Extended Mix",
    "Artist(s)": "FISHER (OZ)",
    "Remixer(s)": "",
    "Duration(sec)": 381,
    "Duration(min)": "6:21",
    "BPM": 126,
    "Key": "F min",
    "Label": "Catch & Release",
    "Released": "2022-09-02",
    "Image Links": "https://geo-media.beatport.com/image_size/1400x1400/594a3d53-5194-46f9-8ad6-5ff3f5dc4eb0.jpg",
    "Preview": "https://geo-samples.beatport.com/track/8de19c7f-ad00-47a0-ba26-f8912875284c.LOFI.mp3"
}
```

### Beatport Genre Crawler
Will crawl Beatport and scrape each Genre's Top100 chart.
```bash
python emd/beatport/genre_crawler.py --preview
```
`--preview`: Will download the LoFi Preview mp3 of the tracks

### Spotify Playlist Scraper
It will save the track information of the playlist with provided URI<br>
If output_dir not provided, to Playlists/playlist_name
```bash
python emd/spotify/playlist_scraper.py -u=<URI>
```

### Traxsource Top100 Chart Scraper
Scrapes metadata.
```bash
python emd/traxsource/chart_scraper.py -u=<URL> --analyze --save-figure
```
`--analyze`: Will perform Key, BPM, Label, Artist analysis<br>
`--save-figure`: Will save these figures<br>

### Traxsource Genre Crawler
Will crawl Traxsource and scrape each Genre's Top100 chart.
```bash
python emd/traxsource/genre_crawler.py
```

### Youtube Searcher
```bash
python/youtube/youtube_searcher.py -p=<chart_or_playlist_json_path> -N=5
```
`-N`: determines the depth of the youtube search for a query

### Youtube mp3 Downloader
It will try to download the best possible bit rate, which is 128 kbps for Youtube.
```bash
python emd/youtube/mp3_downloader.py -u=<track_or_playlist_youtube_URL> --clean
```
`--clean`: after a track is downloaded its name will be cleaned and formatted<br>

### Chart and Playlist Downloader
Downloads all the tracks in the query.json file
```bash
python/youtube/download_queries.py -p=<queries_json_path> --clean
```
`--clean`: after a track is downloaded its name will be cleaned and formatted<br>

### Chart Analysis
Can analyze the Top100 Charts of Beatport and Traxsource. You need to scrape the chart first with [Beatport](#beatport-top100-chart-scraper) or, [Traxsource](#traxsource-top100-chart-scraper)<br>
Perform Key, BPM, Label, Artist analysis and plot their distributions
```bash
python emd/analyze_chart.py -p=<chart_json_path> --save-figure
```
