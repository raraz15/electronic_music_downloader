import os
import sys
import argparse
import traceback
import re
import json

from youtubesearchpython import VideosSearch

from info import CHARTS_DIR,QUERY_DIR # Default download directories

# TODO: start with no Mix information!
def form_query(track_dict):
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

def get_best_link_for_track(customSearch, query, artist, label, audio_duration):
    artist,label=artist.lower(),label.lower()
    results=customSearch.result()['result']
    if results:  # If there is a match, search for good links
        # For each result, look for quality by cidence measure
        for result in results:
            # Get the 3 key information
            description=result['descriptionSnippet']
            channel_name=result['channel']['name'].lower()
            video_duration=duration_str_to_int(result['duration'])
            link=result['link']
            c=() # Will store the confidence values of a result
            # 1) Check if "'provided to youtube " exists in description
            flag=True
            if description:
                for text in description:
                    if re.search(r"provided to youtube", text['text'].lower()):
                        c+=(True,)
                        flag=False
                        break
                if flag:
                    c+=(False,)
            else: # No description
                c+=(False,)
            # 2) Check if artist or label uploaded the video
            if re.search(r'{}'.format(artist), channel_name) or re.search(r'{}'.format(label), channel_name):
                c+=(True,)
            else:
                c+=(False,)
            # 3) Compare the video and track lengths
            dur_diff=abs(video_duration-audio_duration)
            if dur_diff>10:
                c+=(False,)
            else:
                c+=(True,)

            # Choose the best link
            if c[1] or (c[0] and (not c[1])): # A good match is found
                if c[2]: # The match has good duration
                    best_link=link
                    print('Success for: {}\n{}'.format(query, best_link))
                    break
                else: # A different mix type
                    best_link=link
                    # TODO:  change the query ? 
                    print('Found a mix from the artist or the label but with wrong duration.')
                    print(f"{query} - {best_link}")
                    print(f"Video duration: {video_duration} - Track duration: {audio_duration}")
                    break 
            else:
                best_link=""
        if best_link=="":
            print("No link from the artist or one provided to youtube was found.")
            print(query)            
    else: # No match for the query    
        best_link=""
        print(f"Search Failed for: {query}")
        
    return best_link, query

def find_link_single_track(track_dict, N, idx=None):
    """Takes a single track dict, and makes a query to Youtube."""
    if idx is not None: 
        print("-"*30+f"{idx+1}"+"-"*30)
    query=form_query(track_dict) 
    try:
        customSearch=VideosSearch(query, limit=N)
        link, query=get_best_link_for_track(customSearch, 
                                            query,
                                            track_dict['Artist(s)'],
                                            track_dict['Label'],
                                            duration_str_to_int(track_dict['Duration']))
        return link, query
    except KeyboardInterrupt:
        sys.exit()
    #except SystemExit:
    #    print('Sys exit took me here.')
    except Exception as ex:     
        print("There was an error on: {}".format(query))
        exception_str=''.join(traceback.format_exception(etype=type(ex), value=ex, tb=ex.__traceback__))
        print(exception_str+'\n')

# TODO: UTF before making a query! or enforce it in beatport_analyzer!!
# TODO: (opt) Output directory?
# TODO: deal with - (Official Audio), ...
# TODO: Premiere
if __name__ == '__main__':

    parser=argparse.ArgumentParser(description='Youtube Searcher from Beatport chart')
    parser.add_argument('-p', '--path', type=str, required=True, help='Path to the chart_dict.json file.')
    parser.add_argument('-N', type=int, default=3, help='Number of top entries to search for each query.')
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
        link, query=find_link_single_track(track_dict, args.N, i)
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