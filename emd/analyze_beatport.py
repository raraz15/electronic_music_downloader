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
from collections import defaultdict

import matplotlib.pyplot as plt

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

def make_name(name_dict_list):
    name=", ".join([artist["name"] for artist in name_dict_list])
    name=unicodedata.normalize('NFKD', name).encode('ascii', 'ignore') # Replace é with e
    name=name.decode("utf-8") # For json dump
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
        track_dicts[i]={'Title': track["release"]["name"],
                      'Mix': track["mix"],
                      'Artist(s)': make_name(track["artists"]),
                      'Remixers': make_name(track["remixers"]),
                      'Duration': track["duration"]["minutes"],
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
    parser.add_argument('--save-figure', action='store_true', help='Save the figures.')
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
    max_title_len=max([len(track['Title']) for i,track in enumerate(tracks.values()) if i<args.N])
    max_artist_len=max([len(track['Artist(s)']) for i,track in enumerate(tracks.values()) if i<args.N])
    print(f"Top {args.N} Tracks:")
    print(f"| {'#':>2} | {'Title':^{max_title_len}s} | {'Artist(s)':^{max_artist_len}s} |")
    print("-"*(3+3+2+3+1+max_title_len+max_artist_len))
    for i in range(1,args.N+1):
        title=tracks[i]['Title']
        artists=tracks[i]['Artist(s)']
        print(f"| {i:>2} | {title:<{max_title_len}} | {artists:<{max_artist_len}} |")
    print("-"*(3+3+2+3+1+max_title_len+max_artist_len))

    # Analysis
    key_dict,bpm_dict,label_dict,artist_dict=defaultdict(int),defaultdict(int),defaultdict(int),defaultdict(int)
    remix_dict={'remix': 0, 'original': 0}
    for track in tracks.values():
        bpm_dict[track['BPM']] += 1
        key_dict[track['Key']] += 1
        label_dict[track['Label']] += 1
        for artist in track['Artist(s)'].split(','):
            artist_dict[artist.replace("$$","\$\$")] += 1  # One artist' name included $$ which was bad for OS           
        if 'Remixer(s)' in track:
            remix_dict['remix'] += 1
        else:
            remix_dict['original'] += 1
    artist_dict=dict(sorted(artist_dict.items()))
    key_dict=dict(sorted(key_dict.items()))               
    bpm_dict=dict(sorted(bpm_dict.items()))
    label_dict=dict(sorted(label_dict.items())) 

    # Plotting
    # Pie chart, where the slices will be ordered and plotted counter-clockwise:
    labels=['Remix', 'Original']
    explode=(0, 0.05)  
    fig0, ax=plt.subplots(figsize=(10,5))
    ax.pie(remix_dict.values(), explode=explode, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90, textprops={'fontsize': 15})
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    ax.set_title(f"Beatport {SIMPLE_NAME} Top100 Remix Distribution",fontsize=14)
    if not args.save_figure:
        plt.draw()   

    fig1, ax=plt.subplots(figsize=(20,8))
    ax.bar(artist_dict.keys(), artist_dict.values())
    ax.set_ylabel('Number of Appearances',fontsize=15)
    ax.set_xlabel('Artist',fontsize=15)
    ax.set_title(f"Beatport {SIMPLE_NAME} Top100 Artist Distribution",fontsize=14)
    plt.xticks(rotation=90)
    if not args.save_figure:
        plt.draw()    

    fig2, ax=plt.subplots(figsize=(20,8))
    ax.bar(key_dict.keys(), key_dict.values())
    ax.set_ylabel('Number of Tracks',fontsize=15)
    ax.set_xlabel('Track Key',fontsize=15)
    ax.set_title(f"Beatport {SIMPLE_NAME} Top100 Key Distribution",fontsize=14)
    if not args.save_figure:
        plt.draw()  

    fig3, ax=plt.subplots(figsize=(20,8))
    ax.bar(bpm_dict.keys(), bpm_dict.values())
    ax.set_ylabel('Number of Tracks',fontsize=15)
    ax.set_xlabel('Track BPM',fontsize=15)
    ax.set_title(f"Beatport {SIMPLE_NAME} Top100 BPM Distribution",fontsize=14)
    if not args.save_figure:
        plt.draw()   

    fig4, ax=plt.subplots(figsize=(20,8))
    ax.bar(label_dict.keys(), label_dict.values())
    ax.set_ylabel('Number of Tracks',fontsize=15)
    ax.set_xlabel('Label Name',fontsize=15)
    ax.set_title(f"Beatport {SIMPLE_NAME} Top100 Label Distribution",fontsize=14)
    plt.xticks(rotation=90)
    if not args.save_figure:
        plt.draw()
        plt.show()        

    # If the user required further analysis
    if args.save_figure:
        fig0.savefig(os.path.join(output_dir, f"{CHART_NAME}-Remix_Distribution.png"))
        fig1.savefig(os.path.join(output_dir, f"{CHART_NAME}-Artist_Distribution.png"))
        fig2.savefig(os.path.join(output_dir, f"{CHART_NAME}-Key_Distribution.png"))
        fig3.savefig(os.path.join(output_dir, f"{CHART_NAME}-BPM_Distribution.png"))
        fig4.savefig(os.path.join(output_dir, f"{CHART_NAME}-Label_Distribution.png"))
        plt.close("all")
