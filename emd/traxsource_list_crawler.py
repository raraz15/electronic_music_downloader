import os
import re
import json
import requests
from bs4 import BeautifulSoup
import argparse
import datetime as dt

from scrape_traxsource import scrape_track
from info import CRAWL_DIR

HOME_URL='https://www.traxsource.com'
LIST_URL=f'{HOME_URL}/label/12809/essential-tech?cn=tracks'

DATE=dt.datetime.strftime(dt.datetime.now(),"%d_%m_%Y")

def crawl_single_page(url):
    # Load the page
    html=requests.get(url).content
    bsObj=BeautifulSoup(html, 'lxml')
    # Scrape each track in the page
    tracks={}
    for i,track_soup in enumerate(bsObj.findAll("div", {"data-trid":re.compile("[0-9]*")})):
        url_ext=track_soup.find('div', {'class': 'trk-cell title'}).find('a').attrs['href']
        track_url=HOME_URL+url_ext
        try:
            tracks[i]=scrape_track(track_url)
        except:
            print(f"{track_url} couldn't be scraped.")
            pass
    return tracks

if __name__=='__main__':

    parser=argparse.ArgumentParser(description='Traxsource List Crawler')
    parser.add_argument('-o', '--output', type=str, default='', help='Specify an output directory.')
    args=parser.parse_args()

    # Get the name of the playlist
    list_name=LIST_URL.split("/")[-1].split("?")[0].title().replace('-','_')
    print(list_name)
    list_name=f"{list_name}-TraxsourceCrawl-{DATE}"

    # Find the number of pages
    html=requests.get(LIST_URL).content
    bsObj=BeautifulSoup(html, 'lxml')
    N_pages=int(bsObj.find("div", {"class": "page-nums"}).find("a", {"class": "large"}).text)

    # Crawl each page
    print("Starting to crawl...")
    track_dicts={}
    for page_idx in range(1,N_pages+1):
        print(f'Page {page_idx}/{N_pages}')
        url=f'{LIST_URL}&page={page_idx}'
        track_dicts[page_idx]=crawl_single_page(url)
    print("Crawl finished.")

    # If user specified a directory, overwrite the default
    if args.output!='':
        output_dir=args.output
    else:
        output_dir=os.path.join(CRAWL_DIR,list_name)
	# Create the Output Directory
    os.makedirs(output_dir, exist_ok=True)
    # Export to json
    output_path=os.path.join(output_dir,list_name+".json")
    with open(output_path,'w', encoding='utf8') as outfile:
        json.dump(track_dicts, outfile, indent=4)
    print(f"Exported the crawl result to: {output_path}")