import os
import sys
import json
import argparse
import traceback
from concurrent.futures import ThreadPoolExecutor
import youtube_dl

QUERY_DIR='Queries'
DOWNLOAD_DIR='Downloads'

#def download_single_track(query_dict, download_dir):
#
#    ydl_opts = {
#        'format': 'bestaudio/best',
#        'postprocessors': [{
#        'key': 'FFmpegExtractAudio',
#        'preferredcodec': 'mp3',
#        'preferredquality': '320',},
#        ],
#        'outtmpl': os.path.join(download_dir, '{}.mp3'.format(query_dict['Query']))}
#    
#    try:
#        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
#            ydl.download([query_dict['Link']])
#    except KeyboardInterrupt:
#        sys.exit(1)
#    except Exception as ex:     
#        print("There was an error on: {}".format(query_dict['Link']))
#        exception_str = ''.join(traceback.format_exception(etype=type(ex), value=ex, tb=ex.__traceback__))
#        print(exception_str+'\n')

#def download_all_links_and_queries(queries_dict, download_dir):
#    os.makedirs(download_dir, exist_ok=True)
#    print(f"Downloading to: {download_dir}")    
#    with ThreadPoolExecutor(max_workers=10) as executor: # Download all with multiple threads
#        for i, query_dict in enumerate(queries_dict.values()):
#            if not i % 100:
#                print('\n{:.1f}% ({}/{})'.format(100*(i)/len(queries_dict), i, len(queries_dict)))
#            future = executor.submit(download_single_track, query_dict, download_dir)
#            print(future.result())

#def download_all_links_and_queries(queries_dict, download_dir):
#    with ThreadPoolExecutor(max_workers=10) as executor: # Download all with multiple threads
#        for i, query_dict in enumerate(queries_dict.values()):
#            if not i % 100:
#                print('\n{:.1f}% ({}/{})'.format(100*(i)/len(queries_dict), i, len(queries_dict)))
#            future = executor.submit(download_single_track, query_dict, download_dir)
#            print(future.result())

# TODO: add doptional download path
if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Youtube mp3 downloader from queries.json.')
    parser.add_argument('-q', '--queries', type=str, required=True, help='Directory to the queries.json file.')
    args = parser.parse_args()

    # Load the queries
    query_path = args.queries
    if not os.path.isfile(query_path): # if just the name of the json file is given
        query_path = os.path.join(QUERY_DIR, query_path)
    with open(query_path, 'r') as infile:
        queries_dict = json.load(infile)
    
    # Determine the export directory
    query_name = os.path.splitext(os.path.basename(query_path))[0]
    download_dir = os.path.join(DOWNLOAD_DIR, query_name)

    # Download all the tracks
    for i, query_dict in enumerate(queries_dict.values()):
        if i==0:
            os.system(f"python mp3_downloader/mp3_downloader.py -l={query_dict['Link']} -o={download_dir} -v")
        else:
            os.system(f"python mp3_downloader/mp3_downloader.py -l={query_dict['Link']} -o={download_dir}")