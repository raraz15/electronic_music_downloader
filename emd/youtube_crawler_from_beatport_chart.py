import os
import sys
import argparse
import traceback
import re
import json
from concurrent.futures import ThreadPoolExecutor

import numpy as np

from youtubesearchpython import VideosSearch

from info import CHARTS_DIR,QUERY_DIR # Default download directories

# TODO: deal with - (Official Audio), ...
# TODO: Premiere
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

def get_best_link_for_track(customSearch, query, artist, label, audio_duration, conservative=False):

    artist=artist.lower()
    label=label.lower()
        
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
            if re.search(r'{}'.format(artist), channel_name) or re.search(r'{}'.format(label), channel_name):
                confidence_list[i] += (1,)
                flag=False
            if flag:
                confidence_list[i] += (0,)   
              
            # 3) Check if video length is correct
            video_duration=customSearch.result()['result'][i]['duration']
            duration_differences.append(abs(duration_str_to_int(video_duration)-audio_duration))    

        # score the confidence tupples
        scores=np.array([2*c[0]+c[1] for c in confidence_list])
        if not np.any(scores): # if all have zero confidence, do not download!
            print("Found links failed all download criteria for query: {}".format(query))
            best_link=""
        else:
            best_link_idx=np.argmax(scores)
            if duration_differences[best_link_idx] > 180:
                print("Links has terrible length for query: {} with length diff: {}".format(query,
                    duration_differences[best_link_idx]))
                print('Corresponding Link: {}'.format(links[best_link_idx]))
                best_link=""
            elif duration_differences[best_link_idx] <= 180 and duration_differences[best_link_idx] > 5:
                print('Found a mix from the artist or the label with wrong duration.')
                if not conservative:
                    best_link=links[best_link_idx]
                    query=customSearch.result()['result'][i]['title'] # make the query video title
                else:
                    best_link=""
            else:
                best_link=links[best_link_idx] # select the link with best score
                print('Success for: {}'.format(best_link))
    else: # No match for the query    
        best_link=""
        print("Search Failed for query: {}".format(query))
        
    return best_link, query

def find_link_single_track(track_dict, N, conservative=False):
    """Takes a single track dict, and makes a query to youtube."""

    query=query_title(track_dict) 
    try:
        customSearch=VideosSearch(query, limit=N)
        link, query=get_best_link_for_track(customSearch, 
                                            query,
                                            track_dict['Artist(s)'],
                                            track_dict['Label'],
                                            duration_str_to_int(track_dict['Duration']),
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

def get_all_links_and_queries(chart_dict, N=10, conservative=False):
    """For all the track dicts inside the chart dict, finds the corresponding Youtube links."""

    query_dict={}
    with ThreadPoolExecutor(max_workers=16) as executor:
        for i, track_dict in enumerate(chart_dict.values()): 
            #if not i % 100:
            #    print('\n{:.1f}% ({}/{})'.format(100*(i)/len(chart_dict), i, len(chart_dict)))
            future=executor.submit(find_link_single_track, track_dict, N, conservative)
            if (future.result() is not None) and future.result()[0]: # if non-empty link
                query_dict[i]={**track_dict, **{'Link': future.result()[0], 'Query': future.result()[1]}}
    print("{} links are returned.".format(len(query_dict)))
    return query_dict


# TODO: conservative returning mode (old TODO?)
# TODO: (opt) Output directory?
if __name__ == '__main__':

    parser=argparse.ArgumentParser(description='Youtube Searcher from Beatport chart')
    parser.add_argument('-p', '--path', type=str, required=True, help='Path to the chart_dict.json file.')
    parser.add_argument('-n', type=int, default=3, help='Number of top entries to search for each query.')
    parser.add_argument('--conservative', action='store_true', help='Be conservative during search.')
    args=parser.parse_args()    

    # Load the chart file
    chart_path=args.path
    if not os.path.isfile(chart_path): # if just the name of the json file is given
        chart_path=os.path.join(CHARTS_DIR, chart_path)
    with open(chart_path, 'r') as infile:
        chart=json.load(infile)

    query_dict=get_all_links_and_queries(chart, N=args.n, conservative=args.conservative)

    chart_name=os.path.splitext(os.path.basename(chart_path))[0]
    outfile_name=f"{chart_name}-Queries.json"
    outfile_path=os.path.join(QUERY_DIR, outfile_name)
    with open(outfile_path, 'w', encoding='utf-8') as outfile:
        json.dump(query_dict, outfile, indent=4)