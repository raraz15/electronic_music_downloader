import os
import sys
import json
import requests
import argparse
import datetime as dt
from bs4 import BeautifulSoup

PACKAGE_PATH=os.path.dirname(os.path.realpath(__file__))
LIBRARY_PATH=os.path.dirname(PACKAGE_PATH)
sys.path.append(LIBRARY_PATH)

from chart_scraper import scrape_chart
from utilities import format_genre_string
from info import CRAWL_DIR

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
    print(f"{len(genre_dict)} Genre URLs returned.")

    # If user specified a directory, overwrite the default
    if args.output!='':
        output_dir=args.output
    else:
        output_dir=os.path.join(CRAWL_DIR, f"BeatportTop100-{DATE}")
    os.makedirs(output_dir, exist_ok=True)
    print(f"Charts will be exported to: {output_dir}")

    # Find the Top100 links of each genre, scrape its track information, export
    charts={}
    for genre,url in genre_dict.items():
        print(f"\nRetrieving {genre} Top100 Chart metadata...")
        # Find the top100 page url
        html=requests.get(url).content
        bsObj=BeautifulSoup(html, 'lxml')
        url_top100=f"{url}/top-100"
        # Modify name
        genre=format_genre_string(genre)
        # Get the chart information
        tracks=scrape_chart(url_top100)
        charts[genre]=tracks
        # Export to json
        chart_name=f"{genre}-BeatportTop100-{DATE}"
        output_path=os.path.join(output_dir,chart_name+".json")
        with open(output_path,'w', encoding='utf8') as outfile:
            json.dump(tracks, outfile, indent=4)
        print(f"Exported {len(tracks)} track information to: {output_path}\n")
    # Download the preview mp3s
    if args.preview:
        preview_dir=os.path.join(output_dir,"Preview")
        os.makedirs(preview_dir,exist_ok=True)
        print(f"Preview mp3s will be stored in: {preview_dir}")
        for genre,tracks in charts.items():
            genre_preview_dir=os.path.join(preview_dir,genre)
            os.makedirs(genre_preview_dir,exist_ok=True)
            print(f"Downloading to: {genre_preview_dir}")
            for i,track in tracks.items():
                req=requests.get(track["Preview"])
                with open(os.path.join(genre_preview_dir,f"{track['Title']}.mp3"),"wb") as f:
                    f.write(req.content)
    print("Done!")