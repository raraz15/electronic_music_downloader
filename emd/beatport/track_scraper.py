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

# TODO: retrieve album (will require an extra scrape)
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
    parser.add_argument('--preview', action='store_true', help='Download the preview mp3.')
    args=parser.parse_args()

    # Scrape the information
    print(f"Scraping information from: {args.url}")
    track=scrape_track(args.url)
    print(json.dumps(track,indent=4))
    # If user specified a directory, export the json file
    if args.output!='':
        # Create the Output Directory
        os.makedirs(args.output,exist_ok=True)
        # Export to json
        output_path=os.path.join(args.output,track["Title"]+".json")
        with open(output_path,'w', encoding='utf8') as outfile:
            json.dump(track, outfile, indent=4)
        print(f"Exported the track information to: {output_path}\n")

        # Download the preview mp3 if specified
        if args.preview:
            print(f"Downloading the Preview mp3s to: {args.output}")
            req=requests.get(track["Preview"])
            with open(os.path.join(args.output,f"{track['Title']}.mp3"),"wb") as f:
                f.write(req.content)

    print("Done!")