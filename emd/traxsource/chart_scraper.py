import os
import sys
import re
import json
import datetime as dt
import requests
import argparse
from bs4 import BeautifulSoup

PACKAGE_PATH=os.path.dirname(os.path.realpath(__file__))
LIBRARY_PATH=os.path.dirname(PACKAGE_PATH)
sys.path.append(LIBRARY_PATH)

from track_scraper import scrape_track
from analyze_chart import analyze_and_plot
from info import CHARTS_DIR # Default directory

DATE=dt.datetime.strftime(dt.datetime.now(),"%d_%m_%Y")
HOME_URL="https://www.traxsource.com"

def scrape_chart(url):
    # Load the chart page
    html=requests.get(url).content
    bsObj=BeautifulSoup(html, 'lxml')
    # Find track URLs
    track_urls=[]
    for a in bsObj.findAll("a",{"href":re.compile(r"/track/[0-9]*")}):
        track_urls.append(HOME_URL+a['href'])
    # Get the metadata of each track
    print("Retrieving the metadata...")
    tracks={idx+1: scrape_track(track_url) for idx,track_url in enumerate(track_urls)}
    return tracks

if __name__ == '__main__':

    parser=argparse.ArgumentParser(description='Traxsource Top100 Analyzer')
    parser.add_argument('-u', '--url', type=str, required=True, help='URL of the Top100 site.')
    parser.add_argument('-o', '--output', type=str, default='', help='Specify an output directory.')
    parser.add_argument('-N', type=int, default=10, help='Number of top entries to display.')
    parser.add_argument('-a','--analyze', action='store_true', help='Analyze the chart.')
    parser.add_argument('-s','--save-figure', action='store_true', help='Save the analyzed figures.')
    args=parser.parse_args()

    # Navigate to the Top100 page
    genre_url=args.url
    if genre_url.split("/")[-1]=="top":
        chart_url=genre_url
    else:
        chart_url=genre_url+"/top"

    # Get the Genre Name from the URL
    genre=chart_url.split("/")[-2].title().replace('-','_')
    CHART_NAME=f"{genre}-TraxsourceTop100-{DATE}"
    SIMPLE_NAME=genre.replace('_',' ') # For Plotting and Printing
    print(f"{SIMPLE_NAME} - Top 100")
    
    # Scrape the chart information
    tracks=scrape_chart(chart_url)

    # If user specified a directory, overwrite the default
    if args.output!='':
        output_dir=args.output
    else:
        output_dir=os.path.join(CHARTS_DIR,CHART_NAME)
	# Create the Output Directory
    os.makedirs(output_dir, exist_ok=True)
    # Export to json
    output_path=os.path.join(output_dir,CHART_NAME+".json")
    with open(output_path,'w', encoding='utf8') as outfile:
        json.dump(tracks, outfile, indent=4)
    print(f"Exported the information of {len(tracks)} tracks to: {output_path}\n")

    # Pretty Print Top N
    max_title_len=max([len(track['Title']) for i,track in tracks.items() if i<=args.N])
    max_artist_len=max([len(track['Artist(s)']) for i,track in tracks.items() if i<=args.N])
    print(f"Top {args.N} Tracks:")
    print(f"| {'#':>2} | {'Title':^{max_title_len}s} | {'Artist(s)':^{max_artist_len}s} |")
    print("-"*(3+3+2+3+1+max_title_len+max_artist_len))
    for i in range(1,args.N+1):
        title=tracks[i]['Title']
        artists=tracks[i]['Artist(s)']
        print(f"| {i:>2} | {title:<{max_title_len}} | {artists:<{max_artist_len}} |")
    print("-"*(3+3+2+3+1+max_title_len+max_artist_len))

    # Plotting
    if args.analyze:
        analyze_and_plot(tracks,args.save_figure,output_dir,CHART_NAME)
        print(f"Analysis plots exported to: {output_dir}")

    print("Done!")
