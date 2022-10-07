# electronic_music_downloader

A repository for obtaining metadata about electronic music tracks collected in Beatport and Traxsource Top100 charts and Spotify Playlists. It can make a Youtube search and download medium quality mp3 files of these tracks. It can also crawl Beatport and get metadata for all electronic music genres and plot informative analysis figures. Moreover, it can download the LoFi Preview mp3 files of the Beatport tracks.

## Table of Contents
* [Installation](#installation)
### List of Functions:
* [Get metadata from a Spotify Playlist](#spotify-scraper)
* [Get metadata from a Beatport Top100 Chart](#beatport-top100-chart-scraper)
* [Get metadata from a Traxsource Top100 Chart](#traxsource-top100-chart-scraper)
* [Analyze and plot distributions of a Top100 Chart](#beatport-chart-analysis)
* [Download LoFi Beatport Preview mp3 files of a Top100 Chart](#beatport-top100-chart-scraper)
* [Crawl Beatport to get metadata and Preview mp3 files of all Top100 Charts (genre-by-genre)](#beatport-crawler)
* [Crawl Traxsource to get metadata of all Top100 Charts  (genre-by-genre) or curated lists](#traxsource-crawler)
* [Make a Youtube search to find tracks uploaded to Youtube by the Artist or Label](#youtube-searcher)
* [Download mp3 files only if original sampling rate>44.1kHz with preferably 128kbps at 16 bits](#youtube-mp3-downloader)
### Pipelines
* [Get metadata and download the mp3 files of tracks of a Spotify Playlist with a pipeline](#get-metadata-of-a-spotify-playlist-and-download-mp3-files-from-youtube)
* [Get metadata and download the mp3 files of tracks of a Beatport Top100 Chart with a pipeline](#get-metadata-of-a-beatport-top100-chart-and-download-mp3-files-from-youtube)
### TODO:
- [ ] URL with _ or not?
- [ ] Package structure for each website
- [ ] TraxSource download Preview mp3
- [ ] Put beatport url of each track
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

### Get metadata of a Beatport Top100 Chart and Download mp3 files from Youtube
This pipeline does 3 things in series.
1. Gets the information of the tracks in a Beatport Top100 Chart
2. Makes Youtube searches for finding these tracks.
3. Only downloads the tracks if they satisfy certaion criteria.

```bash
./beatport_chart_download.sh <Top100_Chart_URI>
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
python emd/scrape_beatport.py -u=<URL> --analyze --save-figure --preview
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

### Beatport Chart Analysis
```bash
python emd/analyze_beatport.py -p=<chart_json_path> --save-figure
```
Perform Key, BPM, Label, Artist analysis and plot their distributions

### Beatport Crawler
```bash
python emd/crawl_beatport.py --preview
```
`--preview`: Will download the LoFi Preview mp3 of the tracks

### Spotify Scraper
```bash
python emd/scrape_spotify.py -u=<URI>
```
It will save the track information of the playlist with provided URI<br>
If output_dir not provided Playlists/playlist_name

### Traxsource Top100 Chart Scraper
```bash
python emd/scrape_traxsource.py -u=<URL> --analyze --save-figure
```
`--analyze`: Will perform Key, BPM, Label, Artist analysis<br>
`--save-figure`: Will save these figures<br>

### Traxsource Crawler
```bash
python emd/crawl_traxsource.py
```

### Youtube Searcher
```bash
python/youtube_searcher.py -p=<chart_or_playlist_json_path> -N=5
```
`-N`: determines the depth of the youtube search for a query

### Youtube mp3 Downloader
```bash
python emd/mp3_downloader.py -u=<track_or_playlist_youtube_URL> --clean
```
`--clean`: after a track is downloaded its name will be cleaned and formatted<br>
<br>
It will try to download the best possible bit rate, which is 128 kbps for Youtube.<br>

### Chart and Playlist Downloader
```bash
python/download_queries.py -p=<queries_json_path> --clean
```
Downloads all the tracks in the query.json file<br>
`--clean`: after a track is downloaded its name will be cleaned and formatted<br>
