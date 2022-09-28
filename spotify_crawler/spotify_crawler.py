import os
import re
import requests
import argparse
import datetime as dt
import json

# Information of the Spotify User is stored in this file
CLIENT_INFO_PATH="spotify_client_info.json"
# Some defaults
AUTH_URL='https://accounts.spotify.com/api/token'
DEFAULT_NAME=dt.datetime.strftime(dt.datetime.now(),"%d_%m_%y")
PLAYLIST_DIR='Playlists'

def name_formatter(name, artists):

    artists=', '.join(artists)

    mix_search=re.search(r"\s-\s.*?mix", name.lower())
    if mix_search:
        mix=name[mix_search.start():mix_search.end()]
        mix=re.sub(r"\s-\s", "", mix) # remove the spaces and the hyphen        
        name=name[:mix_search.start()] + name[mix_search.end():] # remove the match from the string
    else:
        mix=''

    edit_search=re.search(r"\s-\s.*?edit", name.lower())
    if edit_search:
        edit=name[edit_search.start():edit_search.end()]
        edit=re.sub(r"\s-\s", "", edit)
        name=name[:edit_search.start()] + name[edit_search.end():] # remove the match from the string
    else:
        edit=''

    title='{} - {}'.format(artists, name)
    if mix:
        title += ' ({})'.format(mix)
    if edit:
        title += ' ({})'.format(edit)

    return title

if __name__ == "__main__":

    parser=argparse.ArgumentParser(description='Track Metadata Getter from a Spotify Playlist.')
    parser.add_argument('-u', '--uri', type=str, required=True, help='Playlist URI.')
    parser.add_argument('-n', '--name', type=str, default=DEFAULT_NAME, help='Name of the playlist.')   
    #parser.add_argument('-c', '--client', type=str, default=CLIENT_INFO_PATH, help='P.')
    args=parser.parse_args()

    # Create the plyalist url
    URI=args.uri.split(':')[-1]
    url='https://api.spotify.com/v1/playlists/{}/tracks'.format(URI)
    # Read the spotify user's information for request
    with open(CLIENT_INFO_PATH, 'r') as infile:
        client_info_dict = json.load(infile)
    # POST
    auth_response=requests.post(AUTH_URL, {
        'grant_type': 'client_credentials',
        'client_id': client_info_dict["CLIENT_ID"],
        'client_secret': client_info_dict["CLIENT_SECRET"],
    })
    # convert the response to JSON
    auth_response_data=auth_response.json()   
    # save the access token
    access_token=auth_response_data['access_token']
    headers={'Authorization': 'Bearer {token}'.format(token=access_token)} 

    # Initial request to see total number of tracks
    r=requests.get(url, headers=headers)
    dct=r.json()
    N=dct['total']
    print('There are: {} tracks in the list.'.format(N))

    # Start crawling
    track_dicts={}
    for i in range((N//100)+1):
        # Spotify can only return 100 tracks at each request,
        # offset 100 tracks until there is no track left
        r=requests.get(url, params={'offset': i*100}, headers=headers)
        dct=r.json()
        for item in dct['items']:
            track=item['track']
            artists=track['artists']
            track_name=track['name'] # string
            album=track['album'] # dict
            artist_names=[artist_dict['name'] for artist_dict in artists]
            track_dicts[track_name]={'Title': name_formatter(track_name, artist_names),
                                    'Artist(s)': artist_names,
                                    'Album Name': album['name'],
                                    'Album Type': album['type'],
                                    'Duration': (track['duration_ms']/1000),
                                    'Release': album['release_date'],
                                    'Images': album['images'],
                                    'Popularity': track['popularity']
                                    }
    print('\n{} tracks are returned.'.format(len(track_dicts)))
    # Export the track dicts in a json file
    playlist_dir=os.path.join(PLAYLIST_DIR, '{}.json'.format(args.name))
    print('\nExporting the playlist to:\n{}'.format(playlist_dir))
    with open(playlist_dir, 'w') as outfile:
        json.dump(track_dicts, outfile, indent=4)                               