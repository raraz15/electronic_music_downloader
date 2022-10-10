import os
import sys
import json
import requests
import argparse
from bs4 import BeautifulSoup

PACKAGE_PATH=os.path.dirname(os.path.realpath(__file__))
LIBRARY_PATH=os.path.dirname(PACKAGE_PATH)
sys.path.append(LIBRARY_PATH)

from utilities import replace_non_ascii,make_name,key_formatter,duration_str_to_int

HOME_PAGE="https://www.beatport.com"

# TODO: Get Preview
def scrape_track(url):

    html=requests.get(url).content
    bsObj=BeautifulSoup(html,'lxml')

    track_soup=bsObj.find("main",{"class":"interior"})
    top_soup=track_soup.find("div",{"class":"interior-top interior-top-track"})
    title_soup=top_soup.find("div",{"class":"interior-title"})
    title_version=title_soup.findAll("h1")
    title=title_version[0].text
    mix=title_version[1].text

    content_soup=bsObj.find("div",{"class":"interior-track-title-parent"})
    artists_remixers_soup=content_soup.findAll("div",{"class","interior-track-artists"})
    if len(artists_remixers_soup)!=2:
        artist_list=[x.text for x in artists_remixers_soup[0].findAll("a")]
        remixers_list=[]
    else:
        artist_list=[x.text for x in artists_remixers_soup[0].findAll("a")]
        remixers_list=[x.text for x in artists_remixers_soup[1].findAll("a")]

    track_content_soup=track_soup.find("ul",{"class":"interior-track-content-list"})
    str_root="interior-track-content-item interior-track-"
    duration=track_content_soup.find("li",{"class":f"{str_root}length"}).find("span",{"class","value"}).text
    released=track_content_soup.find("li",{"class":f"{str_root}released"}).find("span",{"class","value"}).text
    bpm=track_content_soup.find("li",{"class":f"{str_root}bpm"}).find("span",{"class","value"}).text
    key=track_content_soup.find("li",{"class":f"{str_root}key"}).find("span",{"class","value"}).text
    genre=track_content_soup.find("li",{"class":f"{str_root}genre"}).find("a").text
    label=track_content_soup.find("li",{"class":f"{str_root}labels"}).find("a").text

    image=track_soup.find("img",{"class":"interior-track-release-artwork"})["src"]

    return {'Title': replace_non_ascii(title),
            'Mix': mix,
            'Artist(s)': make_name(artist_list),
            'Remixer(s)': make_name(remixers_list),
            'Genre': genre,
            'Duration(sec)': duration_str_to_int(duration),
            'Duration(min)': duration,
            'BPM': int(bpm),
            'Key': key_formatter(key),
            'Label': replace_non_ascii(label),
            'Released': released,
            'URL': url,
            'Image_URL': image,
            #'Preview': track["preview"]["mp3"]["url"]
            }

if __name__ == '__main__':

    parser=argparse.ArgumentParser(description='Beatport Track Scraper')
    parser.add_argument('-u', '--url', type=str, required=True, help='Track URL.')
    parser.add_argument('-o', '--output', type=str, default='', help='Specify an output directory.')
    #parser.add_argument('--preview', action='store_true', help='Download the preview mp3.')
    args=parser.parse_args()

    print(f"Scraping information from: {args.url}")
    track_dict=scrape_track(args.url)
    print(json.dumps(track_dict,indent=4))