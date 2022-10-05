import os
import re
import json
import argparse
import datetime as dt
import requests
from bs4 import BeautifulSoup

from scrape_traxsource import scrape_track
from info import CRAWL_DIR

DATE=dt.datetime.strftime(dt.datetime.now(),"%d_%m_%Y")
HOME_URL="https://www.traxsource.com"

if __name__=="__main__":

    parser=argparse.ArgumentParser(description='Traxsource Top100 Crawler')
    parser.add_argument('-o', '--output', type=str, default='', help='Specify an output directory.')
    args=parser.parse_args()

    # If user specified a directory, overwrite the default
    if args.output!='':
        output_dir=args.output
    else:
        output_dir=os.path.join(CRAWL_DIR, f"TraxsourceTop100-{DATE}")
    os.makedirs(output_dir, exist_ok=True)
    print(f"Charts will be exported to: {output_dir}")

    # Load the main page
    html=requests.get(HOME_URL).content
    bsObj=BeautifulSoup(html,'lxml')
    # Crawl Through the Genres and scrape the charts
    charts={}
    for split in bsObj.findAll("div",{"class":"mn-split"}): # Two Columns of Genres
        for flt in split.findAll("a",{"class":"flt"}): # For each genre
            # Get the Genre URL
            genre=flt.text
            genre_url_ext=flt["href"]
            chart_url=HOME_URL+genre_url_ext+"/top"
            # Load the Top100 Chart page
            genre_html=requests.get(chart_url).content
            genre_bsObj=BeautifulSoup(genre_html,'lxml')
            # Find track URLs
            track_urls=[]
            for a in genre_bsObj.findAll("a",{"href":re.compile(r"/track/[0-9]*")}):
                track_urls.append(HOME_URL+a['href'])
            # Get the metadata of each track
            print(f"\nRetrieving {genre} Top100 Chart metadata...")
            tracks={idx+1:scrape_track(url) for idx,url in enumerate(track_urls)}
            charts[genre]=tracks
            print(f"Top Track:")
            print(json.dumps(tracks[1],indent=4))
            # Export because slow scraping
            genre=re.sub(r"\s/\s","-",genre)
            genre=re.sub(r"\s&\s","&",genre)
            genre=re.sub(r"\s","_",genre)
            chart_name=f"{genre}-TraxsourceTop100-{DATE}"
            output_path=os.path.join(output_dir,chart_name+".json")
            with open(output_path,'w', encoding='utf8') as outfile:
                json.dump(tracks, outfile, indent=4)
            print(f"Exported chart information to: {output_path}")
