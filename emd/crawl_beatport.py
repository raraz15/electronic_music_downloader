import os
import json
import re
import requests
import argparse
import datetime as dt
from bs4 import BeautifulSoup

from scrape_beatport import split_to_tracks
from info import CHARTS_DIR

URL="https://www.beatport.com"
DATE=dt.datetime.strftime(dt.datetime.now(),"%d_%m_%Y")

if __name__=="__main__":

    parser=argparse.ArgumentParser(description='Beatport Top100 Crawler.')
    parser.add_argument('-o', '--output', type=str, default='', help='Specify an output directory.')
    parser.add_argument('--preview', action='store_true', help='Download the preview mp3.')
    args=parser.parse_args()

    # Find the names and links of genre pages
    html=requests.get(URL).content
    bsObj=BeautifulSoup(html, 'lxml')
    matches=bsObj.find_all("a",{"class": "genre-drop-list__genre"})
    genre_dict={m["data-name"]: f"{URL}/{m['href']}" for m in matches}
    print(f"{len(genre_dict)} genre links returned.")
    print("Finding the Top100 Links...")
    # Find the Top100 links of each genre and scrape its track information
    charts={}
    for genre,url in genre_dict.items():
        # Find the top100 page url
        html=requests.get(url).content
        bsObj=BeautifulSoup(html, 'lxml')
        url_top100=f"{url}/top-100"
        # Modify name
        genre=re.sub(r"\s/\s","-",genre)
        genre=re.sub(r"\s&\s","&",genre)
        genre=re.sub(r"\s","_",genre)
        # Get the chart information
        html=requests.get(url_top100).content
        bsObj=BeautifulSoup(html, 'lxml')
        my_script=bsObj.find("script", {"id": "data-objects"})
        tracks=split_to_tracks(my_script.string)
        charts[genre]=tracks
        print(f"\n{genre} Top Track:")
        print(json.dumps(tracks[1],indent=4))

    # If user specified a directory, overwrite the default
    if args.output!='':
        output_dir=args.output
    else:
        output_dir=os.path.join(CHARTS_DIR, f"Crawl-BeatportTop100-{DATE}")
    os.makedirs(output_dir, exist_ok=True)
    print(f"Exporting the charts to: {output_dir}")

    # Export to json
    for genre,tracks in charts.items():
        chart_name=f"{genre}-BeatportTop100-{DATE}"
        output_path=os.path.join(output_dir,chart_name+".json")
        with open(output_path,'w', encoding='utf8') as outfile:
            json.dump(tracks, outfile, indent=4)
        print(f"Exported {len(tracks)} track information to: {output_path}\n")

    # Download the preview mp3s
    if args.preview:
        preview_dir=os.path.join(output_dir,"Preview")
        os.makedirs(preview_dir)
        print(f"Preview mp3s will be stored in: {preview_dir}")
        for genre,tracks in charts.items():
            genre_preview_dir=os.path.join(preview_dir,genre)
            os.makedirs(genre_preview_dir)
            print(f"Downloading to: {genre_preview_dir}")
            for i,track in tracks.items():
                req=requests.get(track["Preview"])
                with open(os.path.join(genre_preview_dir,f"{track['Title']}.mp3"),"wb") as f:
                    f.write(req.content)

    print("Done!")