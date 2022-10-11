import os,sys
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

HOME_PAGE="https://www.beatport.com"
DATE=dt.datetime.strftime(dt.datetime.now(),"%d_%m_%Y")

def scrape_chart(url):
    # Load the chart page
    html=requests.get(url).content
    bsObj=BeautifulSoup(html,'lxml')
    # Find the track URLs
    print("Finding the URLs of each track...")
    track_soups=bsObj.findAll("li",{"class":"bucket-item ec-item track"})
    url_extensions=[]
    for track_soup in track_soups:
        url_ext=track_soup.find("div",{"class":"buk-track-meta-parent"}).find("p",{"class":"buk-track-title"}).a['href']
        url_extensions.append(url_ext)
    if len(url_extensions)!=100:
        print("Couldn't return 100 track URLs!")
        sys.exit()
    # Parse each track
    print("Parsing the tracks...")
    tracks={}
    for i,url_ext in enumerate(url_extensions):
        track_url=HOME_PAGE+url_ext
        tracks[i+1]=scrape_track(track_url)
    print("Top Track:")
    print(json.dumps(tracks[1],indent=4))
    return tracks

if __name__ == '__main__':

    parser=argparse.ArgumentParser(description='Beatport Top100 Analyzer')
    parser.add_argument('-u', '--url', type=str, required=True, help='URL of the Top100 site.')
    parser.add_argument('-o', '--output', type=str, default='', help='Specify an output directory.')
    parser.add_argument('-N', type=int, default=10, help='Number of top entries to display.')
    parser.add_argument('-a','--analyze', action='store_true', help='Analyze the chart.')
    parser.add_argument('-s','--save-figure', action='store_true', help='Save the analyzed figures.')
    parser.add_argument('--preview', action='store_true', help='Download the preview mp3.')
    args=parser.parse_args()

    # Get the Genre Name from the URL
    genre=args.url.split("/")[-3].title().replace('-','_')
    CHART_NAME=f"{genre}-BeatportTop100-{DATE}"
    SIMPLE_NAME=genre.replace('_',' ') # For Plotting and Printing
    print(f"{SIMPLE_NAME} - Top 100")

    # Scrape the chart
    tracks=scrape_chart(args.url)

    # If user specified a directory, overwrite the default
    if args.output!='':
        output_dir=args.output
    else:
        output_dir=os.path.join(CHARTS_DIR, CHART_NAME)
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

    # Download the preview mp3s
    if args.preview:
        preview_dir=os.path.join(output_dir,"Preview")
        os.makedirs(preview_dir,exist_ok=True)
        print(f"Downloading the Preview mp3s to: {preview_dir}")
        for i,track in tracks.items():
            req=requests.get(track["Preview"])
            with open(os.path.join(preview_dir,f"{track['Title']}.mp3"),"wb") as f:
                f.write(req.content)

    print("Done!")