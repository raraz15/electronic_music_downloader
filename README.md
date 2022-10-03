# electronic_music_downloader

A repository for downloading electronic music from YouTube with Spotify and Beatport scraping and crawling capacities. It could be used for other genres of music but our query algorithm is designed for electronic music traditions (House music oriented).

## Main functionalities:
- [ ] Get metadata from a Spotify Playlist
- [ ] Get metadata from a Beatport Top100 Chart
- [ ] Analyze and plot distributions of a Beatport Top100 Chart
- [ ] Download LoFi Beatport Preview mp3s of a Beatport Top100 Chart
- [ ] Crawl Beatport to get metadata and Preview mp3s of all Genres
- [ ] Make a Youtube search to find tracks uploaded to Youtube by the Artist or the Label
- [ ] Download mp3s only if original sampling rate>44.1kHz with preferably 128kbps at 16 bits

## TODO:
- [ ] Path of the dummy client info (before making public)
- [ ] Edit id3tag (update environment)
- [ ] TraxSource crawling

## Installation

### 1) Create the Environment:
```bash
conda create --name emd --file environment.yml
```
Note: if you change the "emd" name, you should change the line 6 at the bash scripts accordingly.

### 2) You will need the ffmpeg for youtube-dl.

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

To get information from your Spotify playlists, you will need the CLIENT_ID,CLIENT_SECRET keys of the user (you). You can get these information following the steps in: https://developer.Spotify.com/documentation/general/guides/authorization/app-settings/

When you have these information, paste them in spotify_client_info.json


## Usage

After completing the installation, you can use the pipeliness or use the python scripts individually. At the moment there are 2 pipelines.

The beatport_chart_download pipeline does 3 things in series.

1. Gets the information of the tracks in a Beatport Top100 Chart
2. Makes Youtube searches for finding these tracks.
3. Only downloads the tracks if they satisfy certaion criteria.

The spotify_playlist_download.sh pipeline does the same as above, with only the exception of it gets the track information from a Spotify playlist. To use this functionality you should follow Installation part 5.

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

### A) Pipelines

#### Get metadata of a Beatport Top100 Chart and Download mp3 files from Youtube

From the terminal,

```bash
./beatport_chart_download.sh <URL_of_the_Top100_Chart>
```

#### Get metadata of a Spotify Playlist and Download mp3 files from Youtube

To get the URI, open Spotify App from your computer, go to the playlist, click on the *more options* key (three dots), come to *share* while holding the **option key** on your keyboard. The *Copy playlist link* button will change to *Copy Spotify URI*.

From the terminal,
```bash
./spotify_playlist_download.sh <URI>
```

### B) Single task python scripts
```python
python emd/scrape_beatport.py -u=<URL> -o=<output_dir> (opt) -N=25 --analyze --save-figure --preview (opt)
```
```python
python emd/analyze_beatport.py -p=<path to chart.json> -o=<output_dir> (opt) --save-figure (opt)
```
    If you specify an output dir the plots will be saved there.
    If you do not specify an output dir but give --save-figure, the plots will be saved next to the chart.json
```python
python emd/crawl_beatport.py -o=<output_dir> (opt) --preview (opt)
```
    If you do not specify an output_dir, it will export the findings in Crawls/BeatportTop100_Date
    If you provide --preview, it will download each preview mp3 inside the output_dir
```python
python emd/scrape_spotify.py -u=<URI> -o=<output_dir> (opt)
```
    It will save the track information of the playlist with URI in the output_dir.
    If output_dir not provided Playlists/playlist_name
```python
python emd/mp3_downloader.py -u=<Youtube track/playlist URL> -o=<output_dir> (opt) --clean (opt)
```
    If --clean is provided, after the track is downloaded its name will be cleaned and formatted.
```python
python/youtube_crawler.py -p=<Path to chart or playlist.json> -N=5 -o=<output_dir> (opt)
```
```python
python/download_queries.py -p=<Path to queries.json> -o=<output_dir> (opt) --clean (opt)
```