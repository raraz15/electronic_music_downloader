import os,sys
import json
import re
import argparse

from mp3_downloader import main

from info import DOWNLOAD_DIR, QUERY_DIR # Default directories


if __name__ == '__main__':

    parser=argparse.ArgumentParser(description='Youtube mp3 downloader from queries.json.')
    parser.add_argument('-p', '--path', type=str, required=True, help='Path to the queries.json file.')
    parser.add_argument('-o', '--output', type=str, default='', help='Specify an output directory name.')
    parser.add_argument('-c', '--clean', action="store_true", help="If clean the names of the files after download.")
    args=parser.parse_args()

    # Load the Query Dict
    query_path=args.path
    if not os.path.isfile(query_path): # Search in the default query dir
        query_path=os.path.join(QUERY_DIR, query_path)
    with open(query_path, 'r') as infile:
        queries_dict=json.load(infile)

    # Determine the export directory
    if args.output!='':
        output_dir=args.output
    else:
        query_name=os.path.splitext(os.path.basename(query_path))[0]
        query_name=re.sub(r'-Queries', '', query_name) # Remove "Queries"
        output_dir=os.path.join(DOWNLOAD_DIR, query_name)
    os.makedirs(output_dir, exist_ok=True)
    print(f"Track(s) will be downloaded to: {output_dir}")

    # Download all the tracks
    for i, query_dict in enumerate(queries_dict.values()):
        print(f"{i+1}/{len(queries_dict)}")
        try:
            main(query_dict['Youtube_URL'], output_dir, verbose=False, clean=args.clean)
        except KeyboardInterrupt:
            sys.exit()
        except Exception as ex: 
            continue # Main will print the error link