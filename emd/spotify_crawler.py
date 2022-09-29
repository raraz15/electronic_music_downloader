import os,sys
import re
import requests
import argparse
import datetime as dt
import json

AUTH_URL='https://accounts.spotify.com/api/token'
DATE=dt.datetime.strftime(dt.datetime.now(),"%d_%m_%y")
PLAYLIST_DIR='Playlists'

# Information of the Spotify User is stored in this file
CLIENT_INFO_PATH="/Users/recep_oguz_araz/Desktop/Projects/spotify_client_info.json"

def title_formater(name, artists):
    """ Puts the Artist, Track Title, Mix Type information in a standard format"""

    artists=', '.join(artists)

    # Find the type of mix (Extended, Original, Club,...)
    mix_search=re.search(r"\s-\s.*?mix", name.lower())
    if mix_search:
        mix=name[mix_search.start():mix_search.end()]
        mix=re.sub(r"\s-\s", "", mix) # remove the spaces and the hyphen        
        name=name[:mix_search.start()] + name[mix_search.end():] # remove the match from the string
    else:
        mix=''

    # Find out if its some artist's edit
    edit_search=re.search(r"\s-\s.*?edit", name.lower())
    if edit_search:
        edit=name[edit_search.start():edit_search.end()]
        edit=re.sub(r"\s-\s", "", edit)
        name=name[:edit_search.start()] + name[edit_search.end():] # remove the match from the string
    else:
        edit=''
    
    # Combine everything
    title='{} - {}'.format(artists, name)
    if mix:
        title += ' ({})'.format(mix)
    if edit:
        title += ' ({})'.format(edit)

    return title


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
        # Spotify can only return 100 tracks at each request,
        # offset 100 tracks until there is no track left
        r=requests.get(f"{URL}/tracks", params={'offset': i*100}, headers=headers)
        playlist_dct=r.json()
        for item in playlist_dct['items']:
            track=item['track']
            artists=track['artists']
            track_name=track['name'] # string
            album=track['album'] # dict
            artist_names=[artist_dict['name'] for artist_dict in artists]
            track_dicts[track_name]={'Title': title_formater(track_name, artist_names),
                                    'Artist(s)': artist_names,
                                    'Album Name': album['name'],
                                    'Album Type': album['type'],
                                    'Duration': (track['duration_ms']/1000),
                                    'Release': album['release_date'],
                                    'Images': album['images'],
                                    'Popularity': track['popularity']
                                    }
    print(f"{len(track_dicts)} Tracks' information is returned.") 
    
    # Export the track dicts in a json file
    output_name=f'{playlist_name}-{DATE}.json'.format()
    output_dir=os.path.join(args.output, output_name)
    os.makedirs(args.output, exist_ok=True)
    print(f'Exporting the playlist to: {output_dir}')
    with open(output_dir, 'w') as outfile:
        json.dump(track_dicts, outfile, indent=4)