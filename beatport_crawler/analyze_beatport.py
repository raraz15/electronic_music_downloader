#!/usr/bin/env python
# coding: utf-8

import os
import json
import datetime as dt
import re
import requests
import argparse

from bs4 import BeautifulSoup

#import matplotlib.pyplot as plt

OUTPUT_DIR="Charts"
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
    
    # Find track Duration
    duration=find_duration(track)

    # Find image links
    image_links=find_image_links(track)

    # Get Release Date
    release_date=find_release_date(track)
    
    # Get Artists
    artists=find_artists(track)
    
    # Get Remixers
    remixer_name=find_remixers(track)

    # Get BPM
    bpm=find_bpm(track)
    
    # Get the key
    key=find_key(track)

    # Get the label
    label=find_label(track)

    # Get the Mix type
    mix_type=find_mix_type(track)
    
    # Get the Title
    title=find_title(track)
    
    track_dict={'Title': title,
              'Mix': mix_type,
              'Duration': duration,
              'Artist(s)':artists,
              'BPM': bpm,
              'Key': key,
              'Label': label,
              'Chart #': idx,
              'Released': release_date,
              'Image Links': image_links
            }
    
    #Check if remixer exists
    if remixer_name != '':
        track_dict['Remixer(s)']=remixer_name
        
    return track_dict

if __name__ == '__main__':

    parser=argparse.ArgumentParser(description='Beatport Top100 Analyzer')
    parser.add_argument('-o', '--output', type=str, default='', help='Specify an output directory name.')
    parser.add_argument('-u', '--url', type=str, required=True, help='URL of the Top100 site.')
    parser.add_argument('-N', type=int, default=10, help='Number of top entries to display.')
    args=parser.parse_args()

    # Extract the track information
    tracks_garbage=create_tracks_garbage(args.url)
    tracks={idx: create_track_dict(track, idx)  for idx,track in enumerate(tracks_garbage)}
    print("Top Track:")
    print(json.dumps(tracks[0],sort_keys=True,indent=4))

    # If user specified a directory, overwrite the default
    if args.output!='': 
        OUTPUT_DIR=args.output
    else:
        OUTPUT_DIR=os.path.join(OUTPUT_DIR,DATE)
	# Create the Output Directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Export to json
    output_path=os.path.join(OUTPUT_DIR,'Beatport_Top100')
    with open(output_path,'w', encoding='utf8') as outfile:
        json.dump(tracks, outfile, indent=4)
    print(f"\nExported to: {output_path}")

    # Pretty Print Top N
    max_title_len=max([len(track['Title']) for i,track in enumerate(tracks.values()) if i<args.N])
    max_artist_len=max([len(track['Artist(s)']) for i,track in enumerate(tracks.values()) if i<args.N])
    print(f"Top {args.N} Tracks:")
    print(f"| {'#':>2} | {'Title':<{max_title_len}} | {'Artist(s)':<{max_artist_len}} |")
    print("-"*(3+3+2+3+1+max_title_len+max_artist_len))
    for i in range(args.N):
        title=tracks[i]['Title']
        artists=tracks[i]['Artist(s)']
        print(f"| {i+1:>2} | {title:<{max_title_len}} | {artists:<{max_artist_len}} |")
    print("-"*(3+3+2+3+1+max_title_len+max_artist_len))