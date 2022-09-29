import os
import sys
import argparse
import traceback
import re
import json

import numpy as np

from youtubesearchpython import VideosSearch

# Default download directories
from info import PLAYLIST_DIR,QUERY_DIR

def duration_str_to_int(duration_str):
    s=duration_str[-2:]
    m=duration_str[-5:-3]
    duration=int(s) + 60*int(m)    
    if len(duration_str.split(':'))>2:
        h=int(duration_str[:duration_str.index(':')])
        duration += 3600*h
    return duration

# TODO: artist list search?
def get_best_link_for_track(customSearch, query, artists_list, audio_duration, conservative=False):

    artists_list=[artist.lower() for artist in artists_list]
        
    # if there is a match, search for links
    if customSearch.result()['result']:   
        N=len(customSearch.result()['result']) # number of results
        links=[customSearch.result()['result'][i]['link'] for i in range(N)] # Get the relevant links

        # for each result, look for quality by confidence measure
        confidence_list, duration_differences =[], []
        for i in range(N): 
            # 1) Check if "'provided to youTube " exists in description
            flag=True            
            if customSearch.result()['result'][i]['descriptionSnippet']:
                for text in customSearch.result()['result'][i]['descriptionSnippet']:
                    if  re.search(r"provided to youtube", text['text'].lower()):
                        confidence_list.append((1,))
                        flag=False
                        continue
                if flag:
                    confidence_list.append((0,))                    
            else:
                confidence_list.append((0,)) # No description is sketchy
                
            # 2) Check if artist or label uploaded the video
            flag=True
            channel_name=customSearch.result()['result'][i]['channel']['name'].lower()
            # Search for each artist's name in the channel name
            artist_search=[re.search(r'{}'.format(artist), channel_name) for artist in artists_list]
            if np.any(artist_search):
                confidence_list[i] += (1,)
                flag=False
            if flag:
                confidence_list[i] += (0,)   
              
            # 3) Check if video length is correct
            if customSearch.result()['result'][i]['duration'] is not None:
                video_duration=duration_str_to_int(customSearch.result()['result'][i]['duration'])
                duration_differences.append(abs(video_duration-audio_duration))    
            else:
                continue # some weird error
            
        # score the confidence tupples
        scores=np.array([2*c[0]+c[1] for c in confidence_list])
        if not np.any(scores): # if all have zero confidence, do not download!
            print(f"\nReturned links failed all download criteria for: {query}")
            best_link=""
        else:
            best_link_idx=np.argmax(scores)
            if duration_differences[best_link_idx] > 240:
                print("\nLinks has terrible length for query: {} with length diff: {}".format(query,
                    duration_differences[best_link_idx]))
                print(f'Corresponding Link: {links[best_link_idx]}')
                best_link=""
            elif duration_differences[best_link_idx] <= 240 and duration_differences[best_link_idx] > 5:
                print('\nFound a mix from the artist or the label but with wrong duration.')
                if not conservative:
                    best_link=links[best_link_idx]
                    query=customSearch.result()['result'][i]['title'] # make the query video title
                    print(f'Non-conservative mode. Downloading: {best_link}')
                else:
                    best_link=""
                    print(f'Conservative Mode. Skipping: {best_link}')
            else:
                best_link=links[best_link_idx] # select the link with best score
                print('\nSuccess for: {}'.format(best_link))
    else: # No match for the query    
        best_link=""
        print("\nSearch Failed for query: {}".format(query))    

    return best_link, query

def find_link_single_track(track_dict, N, conservative=False):
    """Takes a single track dict, and makes a query to Youtube."""

    query=track_dict['Title']
    try:
        customSearch=VideosSearch(query, limit=N)
        link, query=get_best_link_for_track(customSearch, 
                                            query,
                                            track_dict['Artist(s)'],
                                            track_dict['Duration'],
                                            conservative)
        return link, query
    except KeyboardInterrupt:
        sys.exit()
    except SystemExit:
        print('sys exit took me here.')
    except Exception as ex:     
        print("There was an error on: {}".format(query))
        exception_str=''.join(traceback.format_exception(etype=type(ex), value=ex, tb=ex.__traceback__))
        print(exception_str+'\n')        

if __name__ == '__main__':

    parser=argparse.ArgumentParser(description='Youtube Link Searcher from Spotify Playlist.')
    parser.add_argument('-p', '--playlist', type=str, required=True, help='Path to the playlist_dict.json file.')
    parser.add_argument('-N', type=int, default=3, help='Number of top entries to search for each query.')
    parser.add_argument('--conservative', action='store_true', help='Be conservative during search.')
    args=parser.parse_args()    

    # Load the playlist file
    playlist_path=args.playlist
    if not os.path.isfile(playlist_path): # if just the name of the json file is given
        playlist_path=os.path.join(PLAYLIST_DIR, playlist_path)
    with open(playlist_path, 'r') as infile:
        playlist=json.load(infile)
    print("Playlist loaded.")

    # Create a dict containing queries for each of the tracks in the playlist. 
    print("Making queries for each of the tracks...")
    query_dict={}
    for i, track_dict in enumerate(playlist.values()):
        link, query=find_link_single_track(track_dict, args.N, args.conservative)
        query_dict[i]={**track_dict, **{'Link': link, 'Query': query}}
    print("\n{} links are returned in total.".format(len(query_dict)))

    # Export the query dict
    outfile_name=os.path.splitext(os.path.basename(playlist_path))[0]+'-Queries.json' 
    outfile_path=os.path.join(QUERY_DIR, outfile_name)
    with open(outfile_path, 'w', encoding='utf-8') as outfile:
        json.dump(query_dict, outfile, indent=4)
    print(f"Exported the queries to: {outfile_path}")