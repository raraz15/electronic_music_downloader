#!/usr/bin/env python
# coding: utf-8

import os
import re
import shutil
import argparse
import datetime as dt

import youtube_dl

from info import DOWNLOAD_DIR # Default dir

DATE=dt.datetime.strftime(dt.datetime.now(),'%d_%m_%y')
OUTPUT_DIR=os.path.join(DOWNLOAD_DIR,DATE)

SIMPLE_FORMAT=f"%(title)s.%(ext)s"
YDL_OPTS={
		'format': 'bestaudio/best',
		'postprocessors': [{'key': 'FFmpegExtractAudio',
							'preferredcodec': 'mp3',
							}],
		# 'preferredquality': '320' upsamples, not real 320kbps
	}

def clean_file_name(title,output_dir):
	clean_title=re.sub("\s\s+"," ",title)      # Multiple
	clean_title=re.sub("\A\s+","",clean_title) # Leading 
	clean_title=re.sub("\s+\Z","",clean_title) # Trailing
	clean_title=re.sub(r"\s*\(Official.*\)\s*", "",clean_title) # (Official.)
	clean_title=re.sub(r"\s*Official Audio\s*", "", clean_title) # Official.
	clean_title=re.sub(r"\s*Official Video\s*", "", clean_title)
	m=re.search(r"\[.*[M|m]ix\]",clean_title) # Replace [] with ()
	if m:
		clean_title=clean_title[:m.start()]+f"({m[0][1:-1]})"+clean_title[m.end():]
	clean_title=re.sub(r"\s*\[.*\]\s*","",clean_title) # [.]
	clean_title=re.sub(r"\*.*\*","",clean_title) # * *
	clean_title=re.sub(r"\s*[O|o]ut [N|n]ow\s*","",clean_title) # Out Now
	clean_title=re.sub(r"\s*[V|v]isualizer\s*","",clean_title) # Visualizer
	if clean_title!=title:
		print(f"Changing {title} to: {clean_title}")
		shutil.move(f"{output_dir}/{title}.mp3",f"{output_dir}/{clean_title}.mp3")

def main(URL,output_dir,verbose=True,clean=False):
	"""Downloads the youtube mp3 to the output_dir with metadata formatting.
	If its a playlist, first flattens the list.
	"""

	# Initialize the output format
	YDL_OPTS['outtmpl']=f"{output_dir}/{SIMPLE_FORMAT}"

	# Flatten the links if its a playlist
	links=[]
	with youtube_dl.YoutubeDL(YDL_OPTS) as ydl: # Get all the individual links
		result=ydl.extract_info(URL, download=False)
		if 'entries' in result: # Playlist
			for i,_ in enumerate(result['entries']):
				links.append(result['entries'][i]['webpage_url'])
			print("Flattened the playlist.")
		else:
			links=[URL] # Single track
	if verbose:
		print("Starting to download...\n")

	for i,link in enumerate(links):
		if verbose:
			print(f"{i+1}/{len(links)}")
		with youtube_dl.YoutubeDL(YDL_OPTS) as ydl:
			# Get information to determine name formatting
			info_dict=ydl.extract_info(link, download=False)
			# Check the audio sampling rate
			if int(info_dict.get('asr', None))<44100:
				print("Low sampling rate! Skipping.")
				continue
			artist=info_dict.get('artist',None)
			track=info_dict.get('track',None)
			# Change the formatting if artist and track name is specified
			if (artist is not None) and (track is not None):
				form="%(artist)s - %(track)s.%(ext)s"
				YDL_OPTS['outtmpl']=f"{output_dir}/{form}"
				title=f"{artist} - {track}"
			else: # Attempt download with the current format
				title=info_dict.get('title', None)
				try:
					ydl.download([link])
					if clean:
						clean_file_name(title,output_dir)
				except Exception:
					print(f"There was an error on: {link}")
				print("")
				continue
		# Set the new format and Download
		with youtube_dl.YoutubeDL(YDL_OPTS) as ydl:
			try:
				ydl.download([link])
				if clean:
					clean_file_name(title,output_dir)
			except Exception:
				print(f"There was an error on: {link}")
		# Go back to the default format
		YDL_OPTS['outtmpl']=f"{output_dir}/{SIMPLE_FORMAT}"
		print("")

# TODO: change the name to download_mp3
# TODO: faster flattening
# TODO: edit id3tag
if __name__ == '__main__':

	parser=argparse.ArgumentParser(description='Youtube mp3 downloader.')
	parser.add_argument('-u', '--url', type=str, required=True, help='Youtube Playlist/Track URL.')
	parser.add_argument('-o', '--output', type=str, default=OUTPUT_DIR, help='Specify an output directory name.')
	parser.add_argument('-c', '--clean', action="store_true", help="If clean the names of the files after download.")
	args=parser.parse_args()

	# Create the output directory
	os.makedirs(args.output, exist_ok=True)
	print(f"Track(s) will be downloaded to: {args.output}")

	# Download
	main(args.url,args.output,clean=args.clean)