#!/usr/bin/env python
# coding: utf-8

import os
import json
import datetime as dt
import re
import requests
import argparse
from bs4 import BeautifulSoup
from collections import defaultdict

import matplotlib.pyplot as plt

from info import CHARTS_DIR # Default directory
DATE=dt.datetime.strftime(dt.datetime.now(),"%d_%m_%Y")

def create_tracks_garbage(url):
    html=requests.get(url).content
    bsObj=BeautifulSoup(html, 'lxml')
    my_script=bsObj.find("script", {"id": "data-objects"})
    my_string=my_script.string
    tracks_garbage=split_to_tracks(my_string)
    return tracks_garbage

def split_to_tracks(my_string):
    """
    Splits the soup string into tracks.
    """
    
    pattern=r'"artists": \['
    artist_matches=[(m.start(0), m.end(0)) for m in re.finditer(pattern, my_string)]
    track_dict_indices=[(artist_matches[i][0],artist_matches[i+1][0]) for i in range(len(artist_matches)-1)]
    tracks=[my_string[s:e] for s,e in track_dict_indices]
    return tracks

def get_between_two_patterns(track, pattern1, pattern2):
    """
    This method will return the desired string that resides between the two patterns.
    """
    start_idx=re.search(pattern1, track).end()
    end_idx=re.search(pattern2, track[start_idx:]).start()
    return track[start_idx:][:end_idx]

def find_release_date(track):    
    return get_between_two_patterns(track, r'"released": "', r'"}, "duration"')

def find_label(track):        
    return get_between_two_patterns(track, r'"label": .*? "name": "', r'", "slug"')

def find_title(track):  
    return get_between_two_patterns(track, r'"release": .*? "name": "', r'", "slug"')

def find_mix_type(track):    
    return get_between_two_patterns(track, r'"mix": "', r'", "name"')

def find_duration(track):
    duration_idx=re.search(r'"minutes": "',track).end()
    return track[duration_idx:duration_idx+4]

# TODO min/maj vs M/m ??
def key_formatter(key):
    key=re.sub(r'\\u266f', "b", key)
    key=re.sub(r'\\u266d', "#", key)
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

def find_key(track):
    key=get_between_two_patterns(track, r'"key": "', r'", "label":')  
    key=key_formatter(key)
    return key

def find_bpm(track):  
    bpm_idx=re.search(r'"bpm": ', track).end()
    return track[bpm_idx:bpm_idx+3]

def find_image_links(track):
    large_end=re.search(r'"large": .*? "url": "',track).end()
    mid_start, mid_end=re.search(r'"medium": .*? "url": "',track).span()
    link_end=re.search(r'", "width"' ,track[large_end:mid_start]).start()
    large_link=track[large_end:mid_start][:link_end]
    small_start=re.search(r'"small": .*? "url": "',track).start()
    link_end=re.search(r'", "width"' ,track[mid_end:small_start]).start()
    small_link=track[mid_end:small_start][:link_end]
    return (large_link,small_link)

def find_artists(track):
    artists_list_idx=(track.find('"artists": '),track.find(', "audio_format"')) # only gives single artist
    artists= track[artists_list_idx[0]:artists_list_idx[1]]
    artist_garbage_list=artists.split('"name": ')
    total_artist_list=[]
    for garbage in artist_garbage_list[1:]:
        artist_name=garbage.split(', "slug"')[0]
        artist_name= artist_name.replace('"','') # Get rid of quotation marks
        total_artist_list.append(artist_name)
    artists=artists_for_title(total_artist_list)         
    return artists

def artists_for_title(artists_list):
    artist_no=len(artists_list)
    if artist_no == 1:
        artists=artists_list[0]
    elif artist_no>1:
        artists=artists_list[0]
        for i in range(1,artist_no):
            artists += ", {}".format(artists_list[i])
    else:
        print('Not enough artist names!')  
    return artists

def find_remixers(track):
    remixer_name=''
    rmx_idx=track.find('"remixers": ')
    sale_type_idx=track.find('"sale_type": ')
    rmx_garbage=track[rmx_idx:sale_type_idx]
    rmx_garbage2=rmx_garbage.split('"name": ')[-1]
    if rmx_garbage2 != rmx_garbage:
        remixer_name=rmx_garbage2.split(', "slug"')[0]
        remixer_name=remixer_name.replace('"','') # Get rid of quotation marks    
    return remixer_name

def create_track_dict(track, idx): 
    track_dict={'Title': find_title(track),
              'Mix': find_mix_type(track),
              'Duration': find_duration(track),
              'Artist(s)':find_artists(track),
              'BPM': find_bpm(track),
              'Key': find_key(track),
              'Label': find_label(track),
              'Chart #': idx,
              'Released': find_release_date(track),
              'Image Links': find_image_links(track)
            }
    #Check if remixer exists
    remixer_name=find_remixers(track)
    if remixer_name != '':
        track_dict['Remixer(s)']=remixer_name      
    return track_dict

# TODO: Fix the 99 bug
if __name__ == '__main__':

    parser=argparse.ArgumentParser(description='Beatport Top100 Analyzer')
    parser.add_argument('-u', '--url', type=str, required=True, help='URL of the Top100 site.')
    parser.add_argument('-o', '--output', type=str, default='', help='Specify an output directory.')
    parser.add_argument('-N', type=int, default=10, help='Number of top entries to display.')
    parser.add_argument('--save-figure', action='store_true', help='Save the figures.')
    args=parser.parse_args()

    # Get the Genre Name from the URL
    genre=args.url.split("/")[-3].title().replace('-','_')
    CHART_NAME=f"Beatport-{genre}-Top100-{DATE}"
    SIMPLE_NAME=genre.replace('_',' ') # For Plotting and Printing
    print(f"{SIMPLE_NAME} - Top 100")

    # Extract the track information
    tracks_garbage=create_tracks_garbage(args.url)
    tracks={idx+1: create_track_dict(track, idx+1)  for idx,track in enumerate(tracks_garbage)} # Use 1 index
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
