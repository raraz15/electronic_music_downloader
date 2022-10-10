import os
import sys
import json
import requests
import argparse
from bs4 import BeautifulSoup

PACKAGE_PATH=os.path.dirname(os.path.realpath(__file__))
LIBRARY_PATH=os.path.dirname(PACKAGE_PATH)
sys.path.append(LIBRARY_PATH)

from utilities import replace_non_ascii,make_name,key_formatter

HOME_PAGE="https://www.beatport.com"

def scrape_track(url):
    # Load the Page
    html=requests.get(url).content
    bsObj=BeautifulSoup(html,'lxml')
    # Decode the script for fast scraping
    split='{"active":' # How beaport encodes information
    track_str=bsObj.findAll("script",{"type":"text/javascript"})[1].string.split(split)[1]
    loc=track_str.find(";\n")
    track_str=track_str[:loc]   # Remove trailing garbage
    track_str=split+track_str   # Add the initially removed part from the split
    track=json.loads(track_str) # So that json can load it as a dict
    # Format the necessary information
    track={'Title': replace_non_ascii(track["release"]["name"]),
            'Mix': track["mix"],
            'Artist(s)': make_name([x["name"] for x in track["artists"]]),
            'Remixer(s)': make_name([x["name"] for x in track["remixers"]]),
            'Label': replace_non_ascii(track["label"]["name"]),
            'Genre': make_name([x["name"] for x in track['genres']]),
            'Duration(sec)': track["duration"]["milliseconds"]//1000,
            'Duration(min)': track["duration"]["minutes"],
            'BPM': track["bpm"],
            'Key': key_formatter(track["key"]),
            'Released': track["date"]["released"],
            'Track URL': url,
            'Image URL': track["images"]["medium"]["url"],
            'Preview': track["preview"]["mp3"]["url"]
            }
    return track

if __name__ == '__main__':

    parser=argparse.ArgumentParser(description='Beatport Track Scraper')
    parser.add_argument('-u', '--url', type=str, required=True, help='Track URL.')
    parser.add_argument('-o', '--output', type=str, default='', help='Specify an output directory.')
    #parser.add_argument('--preview', action='store_true', help='Download the preview mp3.')
    args=parser.parse_args()

    print(f"Scraping information from: {args.url}")
    track_dict=scrape_track(args.url)
    print(json.dumps(track_dict,indent=4))