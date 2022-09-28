import os
import json
import argparse

QUERY_DIR='Queries'
DOWNLOAD_DIR='Downloads'

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
        print(f"{i+1}/{len(queries_dict)}")
        if i==0:
            os.system(f"python mp3_downloader/mp3_downloader.py -l={query_dict['Link']} -o={download_dir} -v")
        else:
            os.system(f"python mp3_downloader/mp3_downloader.py -l={query_dict['Link']} -o={download_dir}")