import os
import sys
import argparse
import traceback
import re
import json

import numpy as np

from youtubesearchpython import VideosSearch

from info import CHARTS_DIR,QUERY_DIR # Default download directories

def query_title(track_dict):
    
    title=track_dict['Title']
    artist=track_dict['Artist(s)']
    mix=track_dict['Mix']
    
    if mix in title or 'mix' in title or 'Mix' in title:
        query="{} - {}".format(artist, title)   
    else:
        if not ('mix' in mix or 'Mix' in mix): # sometimes the "Mix" is not included
            mix += ' Mix' 
        query="{} - {} ({})".format(artist, title, mix)

    # Remove unwanted parts
    query='-'.join([part for part in query.split('-') if 'Official' not in part])
            
    return query

def duration_str_to_int(duration_str):
    s=duration_str[-2:]
    m=duration_str[-5:-3]
    duration=int(s) + 60*int(m)    
    if len(duration_str.split(':'))>2:
        h=int(duration_str[:duration_str.index(':')])
        duration += 3600*h
    return duration

def get_best_link_for_track(customSearch, query, artist, label, audio_duration, conservative=False, idx=None):
    
    if idx is not None: 
        print("-"*24+f"{idx+1}"+"-"*23)

    artist,label=artist.lower(),label.lower()

    results=customSearch.result()['result']
    if results:  # If there is a match, search for good links
        confidence_list, duration_differences =[], []
        links=[result['link'] for result in results] # Get the relevant links
        # For each result, look for quality by confidence measure
        for result in customSearch.result()['result']:
            # Get the 3 key information
            description=result['descriptionSnippet']
            channel_name=result['channel']['name'].lower()
            video_duration=duration_str_to_int(result['duration'])

            link_confidence=() # Will store the truth values
            # 1) Check if "'provided to youtube " exists in description
            flag=True
            if description:
                for text in description:
                    if re.search(r"provided to youtube", text['text'].lower()):
                        link_confidence+=(1,)
                        flag=False
                        break
                if flag:
                    link_confidence+=(0,)
            else: # No description
                link_confidence+=(0,)
            # 2) Check if artist or label uploaded the video
            if re.search(r'{}'.format(artist), channel_name) or re.search(r'{}'.format(label), channel_name):
                link_confidence+=(1,)
            else:
                link_confidence+=(0,)
            confidence_list.append(link_confidence)
            # 3) Compare the video and track lengths
            print(result['duration'] + f" {result['link']}" +f" {link_confidence}")
            duration_differences.append(abs(video_duration-audio_duration))
        print(confidence_list)

        # Between the found links, find the best one
        scores=np.array([2*c[0]+c[1] for c in confidence_list])
        if np.any(scores):
            best_link_idx=np.argmax(scores)
            if duration_differences[best_link_idx] > 180:
                print(f"Links has terrible duration for: {query}")
                print(f"Video duration: {video_duration}s Track duration: {audio_duration}s")
                print(f'Corresponding Link: {links[best_link_idx]}')
                best_link=""
            elif duration_differences[best_link_idx] <= 180 and duration_differences[best_link_idx] > 5:
                print('Found a mix from the artist or the label but with wrong duration.')
                print(f"{query} video duration: {video_duration}s track duration: {audio_duration}s")
                if not conservative:
                    best_link=links[best_link_idx]
                    query=customSearch.result()['result'][best_link_idx]['title'] # make the query video title
                    print(f'Non-conservative mode. Downloading: {best_link}')
                else:
                    best_link=""
                    print(f'Conservative Mode. Skipping: {best_link}')
            else:
                best_link=links[best_link_idx] # select the link with best score
                print(f"Success: {query} - {best_link}")
        else: # if all have zero confidence, do not download!
            best_link=""
            print(f"Returned links failed all download criteria for: {query}")
    else: # No match for the query    
        best_link=""
        print(f"Search Failed for query: {query}")
        
    return best_link, query

def find_link_single_track(track_dict, N, conservative=False, idx=None):
    """Takes a single track dict, and makes a query to Youtube."""

    query=query_title(track_dict) 
    try:
        customSearch=VideosSearch(query, limit=N)
        link, query=get_best_link_for_track(customSearch, 
                                            query,
                                            track_dict['Artist(s)'],
                                            track_dict['Label'],
                                            duration_str_to_int(track_dict['Duration']),
                                            conservative,
                                            idx)
        return link, query
    except KeyboardInterrupt:
        sys.exit()
    except SystemExit:
        print('sys exit took me here.')
    except Exception as ex:     
        print("There was an error on: {}".format(query))
        exception_str=''.join(traceback.format_exception(etype=type(ex), value=ex, tb=ex.__traceback__))
        print(exception_str+'\n')


# TODO: conservative returning mode (old TODO?)
# TODO: (opt) Output directory?
# TODO: deal with - (Official Audio), ...
# TODO: Premiere
if __name__ == '__main__':

    parser=argparse.ArgumentParser(description='Youtube Searcher from Beatport chart')
    parser.add_argument('-p', '--path', type=str, required=True, help='Path to the chart_dict.json file.')
    parser.add_argument('-N', type=int, default=3, help='Number of top entries to search for each query.')
    parser.add_argument('--conservative', action='store_true', help='Download only the best match of links.')
    args=parser.parse_args()    

    # Load the chart file
    chart_path=args.path
    if not os.path.isfile(chart_path): # if just the name of the json file is given
        chart_path=os.path.join(CHARTS_DIR, chart_path)
    with open(chart_path, 'r') as infile:
        chart=json.load(infile)
    print("Chart loaded.")

    # Create a dict containing queries for each of the tracks in the chart. 
    print("Making queries for each of the tracks...")
    print("="*50)        
    query_dict={}
    for i, track_dict in enumerate(chart.values()):
        #if i > 15:
        #    break
        link, query=find_link_single_track(track_dict, args.N, args.conservative, i)

        if link:
            query_dict[i]={**track_dict, **{'Link': link, 'Query': query}}
    print("="*50)        
    print("\n{} links are returned.".format(len(query_dict)))

    # Export the query dict
    chart_name=os.path.splitext(os.path.basename(chart_path))[0]
    outfile_name=f"{chart_name}-Queries.json"
    outfile_path=os.path.join(QUERY_DIR, outfile_name)
    with open(outfile_path, 'w', encoding='utf-8') as outfile:
        json.dump(query_dict, outfile, indent=4)