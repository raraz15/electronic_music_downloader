import os,sys
import re
import json
import datetime as dt
import requests
import argparse
from bs4 import BeautifulSoup

from scrape_beatport import replace_non_ascii
from info import CHARTS_DIR # Default directory

DATE=dt.datetime.strftime(dt.datetime.now(),"%d_%m_%Y")

# TODO: Utils.py maybe
def duration_str_to_int(duration_str):
    min,sec=duration_str.split(":")
    duration=int(sec) + 60*int(min)
    return duration

# TODO: Analysis
# TODO: Preview
if __name__ == '__main__':

    parser=argparse.ArgumentParser(description='Beatport Top100 Analyzer')
    parser.add_argument('-u', '--url', type=str, required=True, help='URL of the Top100 site.')
    parser.add_argument('-o', '--output', type=str, default='', help='Specify an output directory.')
    parser.add_argument('-N', type=int, default=10, help='Number of top entries to display.')
    args=parser.parse_args()

    # Get the Genre Name from the URL
    genre=args.url.split("/")[-2].title().replace('-','_')
    CHART_NAME=f"{genre}-TraxsourceTop100-{DATE}"
    SIMPLE_NAME=genre.replace('_',' ') # For Plotting and Printing
    print(f"{SIMPLE_NAME} - Top 100")
    
    # Extract the track information
    html=requests.get(args.url).content
    bsObj=BeautifulSoup(html, 'lxml')
    # Find the ids of the tracks
    data_trids=[]
    for tag in bsObj.find_all("div"):
        tag_dct=dict(tag.attrs)
        if 'data-trid' in tag_dct:
            data_trids.append(tag_dct['data-trid'])
    if len(data_trids)!=100:
        print("Something went wrong")
        sys.exit()

    # Get the metadata of each track
    print("Retrieving the metadata...")
    tracks={}
    for idx,data_trid in enumerate(data_trids):
        track_tag=bsObj.find("div", {"data-trid": data_trid})
        # Find the url of the track
        url_ext=""
        for tag in track_tag.findAll("div"):
            if 'title' in tag["class"]:
                url_ext=tag.find("a").attrs['href']
                break
        # Reach the track page
        track_html=requests.get("https://www.traxsource.com"+url_ext).content
        track_bsObj=BeautifulSoup(track_html,'lxml')
        # Get track information
        image_link=track_bsObj.find("div", {"class": "tr-image"}).img['src']
        page_head=track_bsObj.find("div", {"class": "page-head"})
        title=page_head.find("h1", {"class": "title"}).string
        version=page_head.find("h1", {"class": "version"}).string
        artists=[t.string for t in page_head.findAll("a", {"class": "com-artists"})]
        artists=", ".join(artists)
        remixers=[t.string for t in page_head.findAll("a", {"class": "com-remixers"})]
        remixers=", ".join(remixers)
        matches=track_bsObj.find("div", {"class": "tr-details"}).find("table").findAll("td")
        for m1,m2 in zip(matches[::2],matches[1::2]):
            m1,m2=m1.string,m2.string
            if m1=="Label:":
                label=m2
            elif m1=="Released:":
                released=m2
            elif m1=="Length:":
                duration=m2
            elif m1=="Genre:":
                genre=m2
            elif m1=="Key:":
                key=m2
            elif m1=="BPM:":
                bpm=m2
        tracks[idx]={'Title': replace_non_ascii(title),
                        'Mix': "" if version is None else version,
                        'Artist(s)': replace_non_ascii(artists),
                        'Remixer(s)': remixers,
                        'Duration(sec)':duration_str_to_int(duration),
                        'Duration(min)': duration,
                        'BPM': int(bpm),
                        'Key': key.split(key[-3:])[0]+" "+key[-3:],
                        'Label': replace_non_ascii(label),
                        'Released': released,
                        'Image Link': bsObj.find("div", {"class": "tr-image"}).img['src'],
                        #'Preview': track["preview"]["mp3"]["url"]
                    }

    # If user specified a directory, overwrite the default
    if args.output!='':
        output_dir=args.output
    else:
        output_dir=os.path.join(CHARTS_DIR,CHART_NAME)
	# Create the Output Directory
    os.makedirs(output_dir, exist_ok=True)
    # Export to json
    output_path=os.path.join(output_dir,CHART_NAME+".json")
    with open(output_path,'w', encoding='utf8') as outfile:
        json.dump(tracks, outfile, indent=4)
    print(f"Exported the information of {len(tracks)} tracks to: {output_path}\n")

    # Pretty Print Top N
    max_title_len=max([len(track['Title']) for i,track in tracks.items() if i<=args.N])
    max_artist_len=max([len(track['Artist(s)']) for i,track in tracks.items() if i<=args.N])
    print(f"Top {args.N} Tracks:")
    print(f"| {'#':>2} | {'Title':^{max_title_len}s} | {'Artist(s)':^{max_artist_len}s} |")
    print("-"*(3+3+2+3+1+max_title_len+max_artist_len))
    for i in range(1,args.N+1):
        title=tracks[i]['Title']
        artists=tracks[i]['Artist(s)']
        print(f"| {i:>2} | {title:<{max_title_len}} | {artists:<{max_artist_len}} |")
    print("-"*(3+3+2+3+1+max_title_len+max_artist_len))

    print("Done!")
