import os
import sys
import re
import json
import argparse
import datetime as dt
import requests
from bs4 import BeautifulSoup

PACKAGE_PATH=os.path.dirname(os.path.realpath(__file__))
LIBRARY_PATH=os.path.dirname(PACKAGE_PATH)
sys.path.append(LIBRARY_PATH)

from chart_scraper import scrape_chart
from utilities import format_genre_string
from info import CRAWL_DIR

DATE=dt.datetime.strftime(dt.datetime.now(),"%d_%m_%Y")
HOME_URL="https://www.traxsource.com"
NON_GENRES=["Sounds, Samples & Loops","DJ Tools","Acapella","Beats","Efx"]

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
            if genre in NON_GENRES: # Some of them are not genres
                continue
            tracks=scrape_chart(chart_url)
            charts[genre]=tracks
            print(f"Top Track:")
            print(json.dumps(tracks[1],indent=4))
            # Export because slow scraping
            genre=format_genre_string(genre)
            chart_name=f"{genre}-TraxsourceTop100-{DATE}"
            output_path=os.path.join(output_dir,chart_name+".json")
            with open(output_path,'w', encoding='utf8') as outfile:
                json.dump(tracks, outfile, indent=4)
            print(f"Exported chart information to: {output_path}")
