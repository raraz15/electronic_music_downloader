import os
import sys
import requests
import argparse
import datetime as dt
import json

PACKAGE_PATH=os.path.dirname(os.path.realpath(__file__))
LIBRARY_PATH=os.path.dirname(PACKAGE_PATH)
sys.path.append(LIBRARY_PATH)

from utilities import replace_non_ascii,make_name
from info import CLIENT_INFO_PATH # Path to json file containing spotify client
from info import PLAYLIST_DIR # Default download directory

AUTH_URL='https://accounts.spotify.com/api/token'
DATE=dt.datetime.strftime(dt.datetime.now(),"%d_%m_%y")

if __name__ == "__main__":

    parser=argparse.ArgumentParser(description='Track Metadata Getter from a Spotify Playlist.')
    parser.add_argument('-u', '--uri', type=str, required=True, help='Playlist URI.')
    parser.add_argument('-o', '--output', type=str, default=PLAYLIST_DIR, help='Specify an output directory.')
    args=parser.parse_args()

    # Read the spotify user's information for request
    with open(CLIENT_INFO_PATH, 'r') as infile:
        client_info_dict=json.load(infile)
    # POST
    auth_response=requests.post(AUTH_URL, {
        'grant_type': 'client_credentials',
        'client_id': client_info_dict["CLIENT_ID"],
        'client_secret': client_info_dict["CLIENT_SECRET"],
    })
    # Convert the response to JSON
    auth_response_data=auth_response.json()
    # Save the access token
    access_token=auth_response_data['access_token']
    headers={'Authorization': 'Bearer {token}'.format(token=access_token)} 

    # Create the playlist URL
    URI=args.uri.split(':')[-1]
    URL=f"https://api.spotify.com/v1/playlists/{URI}"
    # Initial request to see total number of tracks, playlist name
    r=requests.get(URL, headers=headers)
    playlist_dct=r.json()
    playlist_name=playlist_dct["name"]
    print(f"Playlist Name: {playlist_name}")
    N=playlist_dct["tracks"]['total']
    print('There are: {} tracks in the list.'.format(N))

    # Start crawling
    track_dicts={}
    for i in range((N//100)+1):
        # Spotify can only return 100 tracks at each request, offset 100 tracks until there is no track left
        r=requests.get(f"{URL}/tracks", params={'offset': i*100}, headers=headers)
        playlist_dct=r.json()
        for j,item in enumerate(playlist_dct['items']):
            track=item['track']
            track_dicts[i*100+j]={'Title': replace_non_ascii(track['name']),
                                'Artist(s)': make_name([x["name"] for x in track["artists"]]),
                                'Album Name': track['album']['name'],
                                'Album Type': track['album']['type'],
                                'Duration(sec)': track['duration_ms']//1000,
                                'Released': track['album']['release_date'],
                                'Images': track['album']['images'],
                                'Popularity': track['popularity']
                                }
    print(f"{len(track_dicts)} Tracks' information is returned.")

    # Create the output directory
    output_name=f'{playlist_name}-{DATE}'
    os.makedirs(args.output,exist_ok=True)

    # Export the track dicts in a json file
    print(f'Exporting the playlist to: {args.output}')
    with open(os.path.join(args.output,f"{output_name}.json"), 'w') as outfile:
        json.dump(track_dicts, outfile, indent=4)

    # Also create a text file containing the track names
    with open(os.path.join(args.output,f"{output_name}.txt"),"w") as outfile:
        for idx,track_dict in track_dicts.items():
            artist=track_dict["Artist(s)"]
            title=track_dict["Title"]
            track_title=f"{artist} - {title}"
            outfile.write(track_title+"\n")