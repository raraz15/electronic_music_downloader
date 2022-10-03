import os
import sys
import argparse
import traceback
import re
import json

from youtubesearchpython import VideosSearch

from info import QUERY_DIR # Default download directories

def form_query(track_dict):
    title=track_dict['Title']
    artist=track_dict['Artist(s)']
    if 'Label' in track_dict:
        label=track_dict['Label']
        query=f"{title} - {artist} - {label}"
    else:
        query=f"{title} - {artist}"
    return query

def duration_str_to_int(duration_str):
    s=duration_str[-2:]
    m=duration_str[-5:-3]
    duration=int(s) + 60*int(m)
    if len(duration_str.split(':'))>2:
        h=int(duration_str[:duration_str.index(':')])
        duration += 3600*h
    return duration

def get_best_link_for_track(customSearch, query, artist_label, track_dur):
    artist,label=artist_label
    artist,label=artist.lower(),str(label).lower() # Convert to str incase if its None
    results=customSearch.result()['result']
    if results:  # If there is a match, search for good links
        for result in results: # For each result, look for quality by confidence measure
            # Get the 3 key information
            description=result['descriptionSnippet']
            channel_name=result['channel']['name'].lower()
            video_dur=duration_str_to_int(result['duration'])
            link=result['link']
            c=() # Will store the confidence values of a result
            # 1) Check if "'provided to youtube " exists in description
            flag=True
            if description:
                for text in description:
                    if re.search("provided to youtube", text['text'].lower()):
                        c+=(True,)
                        flag=False
                        break
                if flag:
                    c+=(False,)
            else: # No description
                c+=(False,)
            # 2) Check if artist or label uploaded the video
            flag=False
            for a in artist.split(', '):
                flag+=bool(re.search(a, channel_name))
            if flag or re.search(label, channel_name):
                c+=(True,)
            else:
                c+=(False,)
            # 3) Compare the video and track lengths
            dur_diff=abs(video_dur-track_dur)
            if dur_diff>10:
                c+=(False,)
            else:
                c+=(True,)

            # Choose the best link
            if c[1] or (c[0] and (not c[1])): # A good match is found
                if c[2]: # The match has good duration
                    best_link=link
                    print(f"Success for: {query}\n{best_link}")
                    break
                else: # A different mix type
                    best_link=link
                    print('Found a mix from the artist or the label but with wrong duration.')
                    print(f"{query}\n{best_link}")
                    print(f"Video duration: {video_dur}(sec) - Track duration: {track_dur}(sec)")
                    break
            else:
                best_link=""
        if best_link=="":
            print("No link from the artist or one provided to youtube was found.")
            print(query)
    else: # No match for the query
        best_link=""
        print(f"Search Failed for: {query}")
    return best_link

def find_link_single_track(track_dict, N, idx=None):
    """Takes a single track dict, and makes a query to Youtube."""
    if idx is not None:
        print("-"*35+f"{idx+1}"+"-"*35)
    query=form_query(track_dict)
    # Create a tupple of artist and label name
    artist_label=(track_dict['Artist(s)'],)
    if 'Label' in track_dict:
        artist_label+=(track_dict['Label'],)
    else:
        artist_label+=(None,) # Spotify doesn't provide
    try:
        customSearch=VideosSearch(query, limit=N)
        link=get_best_link_for_track(customSearch,
                                    query,
                                    artist_label,
                                    track_dict['Duration(sec)']
                                    )
        return link
    except KeyboardInterrupt:
        sys.exit()
    except Exception as ex:
        print("There was an error on: {}".format(query))
        exception_str=''.join(traceback.format_exception(etype=type(ex), value=ex, tb=ex.__traceback__))
        print(exception_str+'\n')

if __name__ == '__main__':

    parser=argparse.ArgumentParser(description='Youtube Crawler for Electronic Music')
    parser.add_argument('-p', '--path', type=str, required=True, help='Path to the chart_dict.json file.')
    parser.add_argument('-N', type=int, default=5, help='Number of top entries to search for each query.')
    parser.add_argument('-o', '--output', type=str, default=QUERY_DIR, help='Specify an output directory.')
    args=parser.parse_args()

    # Load the chart file
    with open(args.path, 'r') as infile:
        tracks=json.load(infile)
    print("Chart loaded.")

    # Create a dict containing the links for each of the tracks
    print("Making queries for each of the tracks...")
    print("="*70)
    query_dict={}
    for i, track_dict in enumerate(tracks.values()):
        link=find_link_single_track(track_dict, args.N, i)
        if link:
            track_dict["Youtube_URL"]=link
            query_dict[i]=track_dict
    print("="*70)
    print("\n{} links are returned.".format(len(query_dict)))

    # Export the query dict
    tracks_list_name=os.path.splitext(os.path.basename(args.path))[0]
    outfile_name=f"{tracks_list_name}-Queries.json"
    os.makedirs(args.output, exist_ok=True)
    outfile_path=os.path.join(args.output, outfile_name)
    print(f"Exporting to: {outfile_path}")
    with open(outfile_path, 'w', encoding='utf-8') as outfile:
        json.dump(query_dict, outfile, indent=4)