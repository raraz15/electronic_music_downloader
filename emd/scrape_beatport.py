#!/usr/bin/env python
# coding: utf-8

import os
import re
import json
import datetime as dt
import unicodedata
import requests
import argparse
from bs4 import BeautifulSoup

from analyze_beatport import analyze_and_plot
from info import CHARTS_DIR # Default directory

DATE=dt.datetime.strftime(dt.datetime.now(),"%d_%m_%Y")

def key_formatter(key):
    key=re.sub(r'\u266f', "b", key)
    key=re.sub(r'\u266d', "#", key)
    scale_type=key[-3:]
    root=key.split(scale_type)[0]
    if ' ' in root:
        root=root[:root.index(' ')]
    root=sharpen_flats(root)
    if root == 'B#':
        root='C'
    if root == 'E#':
        root='F' 
    key='{} {}'.format(root, scale_type.lower())
    return key

def sharpen_flats(root):
    roots=['C','D','E','F','G','A','B'] 
    if 'b' in root:
        natural_harmonic=root[:1]        
        idx=roots.index(natural_harmonic)
        sharpened_root=roots[idx-1]        
        root="{}#".format(sharpened_root)      
    return root

def replace_non_ascii(str):
    str=unicodedata.normalize('NFKD', str).encode('ascii', 'ignore')
    str=str.decode("utf-8") # For json dump
    return str

def make_name(name_dict_list):
    name=", ".join([artist["name"] for artist in name_dict_list])
    name=replace_non_ascii(name)
    return name

def split_to_tracks(my_string):
    """Splits the soup string into track_dicts."""
    split='{"active":'
    lst=my_string.split(split)
    if len(lst)!=101:
        print("Split went wrong!")
    track_dicts={}
    for i in range(1,101):
        track_str=lst[i]
        if i==100:
            loc=track_str.find(";\n")
            track_str=track_str[:loc] # Remove garbage
        track_str=split+track_str   # Add the removed part from the split
        track_str=track_str[:-2] # Remove the space at the end
        track=json.loads(track_str) # Convert the track soup to dict
        track_dicts[i]={'Title': replace_non_ascii(track["release"]["name"]),
                      'Mix': track["mix"],
                      'Artist(s)': make_name(track["artists"]),
                      'Remixer(s)': make_name(track["remixers"]),
                      'Duration(sec)': track["duration"]["milliseconds"]//1000,
                      'Duration(min)': track["duration"]["minutes"],
                      'BPM': track["bpm"],
                      'Key': key_formatter(track["key"]),
                      'Label': track["label"]["name"],
                      'Released': track["date"]["released"],
                      'Image Links': track["images"]["medium"]["url"],
                      'Preview': track["preview"]["mp3"]["url"]
                    }
    return track_dicts

if __name__ == '__main__':

    parser=argparse.ArgumentParser(description='Beatport Top100 Analyzer')
    parser.add_argument('-u', '--url', type=str, required=True, help='URL of the Top100 site.')
    parser.add_argument('-o', '--output', type=str, default='', help='Specify an output directory.')
    parser.add_argument('-N', type=int, default=10, help='Number of top entries to display.')
    parser.add_argument('-s','--save-figure', action='store_true', help='Save the figures.')
    parser.add_argument('--preview', action='store_true', help='Download the preview mp3.')
    args=parser.parse_args()

    # Get the Genre Name from the URL
    genre=args.url.split("/")[-3].title().replace('-','_')
    CHART_NAME=f"{genre}-BeatportTop100-{DATE}"
    SIMPLE_NAME=genre.replace('_',' ') # For Plotting and Printing
    print(f"{SIMPLE_NAME} - Top 100")

    # Extract the track information
    html=requests.get(args.url).content
    bsObj=BeautifulSoup(html, 'lxml')
    my_script=bsObj.find("script", {"id": "data-objects"})
    tracks=split_to_tracks(my_script.string)
    print("Top Track:")
    print(json.dumps(tracks[1],indent=4))

    # If user specified a directory, overwrite the default
    if args.output!='':
        output_dir=args.output
    else:
        output_dir=os.path.join(CHARTS_DIR, CHART_NAME)
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

    # Plotting
    analyze_and_plot(tracks,args.save_figure,output_dir,CHART_NAME)
    print(f"Analysis plots exported to: {output_dir}")

    # Download the preview mp3s
    if args.preview:
        preview_dir=os.path.join(output_dir,"Preview")
        os.makedirs(preview_dir)
        print(f"Downloading the Preview mp3s to: {preview_dir}")
        for i,track in tracks.items():
            req=requests.get(track["Preview"])
            with open(os.path.join(preview_dir,f"{track['Title']}.mp3"),"wb") as f:
                f.write(req.content)

    print("Done!")