import os
import re
import sys
import json
import requests
import argparse
from bs4 import BeautifulSoup

PACKAGE_PATH=os.path.dirname(os.path.realpath(__file__))
LIBRARY_PATH=os.path.dirname(PACKAGE_PATH)
sys.path.append(LIBRARY_PATH)

from utilities import duration_str_to_int,make_name,replace_non_ascii,format_key

def scrape_track(url):
    """Scrapes information for a single track from url"""

    # Load the track page
    r=requests.get(url)
    if r.status_code==200:
        html=r.content
        bsObj=BeautifulSoup(html,'lxml')
        # Scrape the data
        artists_list=[x.string for x in bsObj.findAll("a", {"class": {"com-artists"}})]
        remixers_list=[x.string for x in bsObj.findAll("a", {"class": {"com-remixers"}})]
        title=bsObj.find("h1", {"class": "title"}).string
        version=bsObj.find("h1", {"class": "version"}).string
        image_link=bsObj.find("div", {"class": "tr-image"}).find("img")['src']
        # Odd elements of the table have the data
        matches=bsObj.find("div", {"class": "tr-details"}).find("table").findAll("td")
        label,released,duration,genre,key,bpm=[r.string for r in matches[1::2]]
        # Get the preview url
        ID = url.split("/")[-2]
        preview_query = f"https://w-static.traxsource.com/scripts/playlist.php?tracks={ID}"
        # Combine
        track={
            'Title': replace_non_ascii(title),
            'Mix': "" if version is None else version,
            'Artist(s)': make_name(artists_list),
            'Remixer(s)': make_name(remixers_list),
            'Label': replace_non_ascii(label),
            'Genre': replace_non_ascii(genre),
            'Duration(sec)':duration_str_to_int(duration),
            'Duration(min)': duration,
            'BPM': int(bpm) if bpm is not None else 0,
            'Key': format_key(key) if key is not None else "",
            'Released': released,
            'Track URL': url,
            'Image URL': image_link,
            'Preview': get_preview(preview_query),
                }
    else:
        track = {}
    return track

def get_preview(preview_query_url):

    r=requests.get(preview_query_url)
    if r.status_code==200:
        html=r.content
        bsObj=BeautifulSoup(html,features='xml')
        text = bsObj.data.string
        # Clean the string and get the url
        text = re.sub("\n", "", text)
        text = re.sub(r"\s\s+"," ", text)
        text = text[2:-2]
        i = text.index("mp3: ")
        text = text[i+len("mp3: "):]
        i = text.index('", ')
        text = text[:i+1]
        return text[1:-1]
    else:
        print("Bad query.")
        return {}

if __name__ == '__main__':

    parser=argparse.ArgumentParser(description='Traxsource Track Scraper')
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