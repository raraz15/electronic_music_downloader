#!/usr/bin/env python
# coding: utf-8

import os
import argparse
import datetime as dt

import youtube_dl

OUTPUT_DIR="Downloads"
DATE=dt.datetime.strftime(dt.datetime.now(),'%d_%m_%y')
OUTPUT_DIR=os.path.join(OUTPUT_DIR,DATE)

SIMPLE_FORMAT=f"%(title)s.%(ext)s"
YDL_OPTS={
		'format': 'bestaudio/best',
		'postprocessors': [{'key': 'FFmpegExtractAudio',
							'preferredcodec': 'mp3',
							}],
		# 'preferredquality': '320' upsamples, not real 320kbps
	}

# TODO: faster flattening
def main(URL,output_dir,verbose=True):
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
			artist=info_dict.get('artist', None)
			track=info_dict.get('track', None)
			# Change the formatting if artist and track name is specified
			if (artist is not None) and (track is not None):
				form="%(artist)s - %(track)s.%(ext)s"
				YDL_OPTS['outtmpl']=f"{output_dir}/{form}"
			else: # Attempt download with the current format
				try:
					ydl.download([link])
				except Exception:
					print(f"There was an error on: {link}")
				print("")
				continue
		# Set the new format and Download
		with youtube_dl.YoutubeDL(YDL_OPTS) as ydl:
			try:
				ydl.download([link])	
			except Exception:
				print(f"There was an error on: {link}")
		# Go back to the default format
		YDL_OPTS['outtmpl']=f"{output_dir}/{SIMPLE_FORMAT}"
		print("")	

if __name__ == '__main__':

	parser=argparse.ArgumentParser(description='Youtube mp3 downloader.')
	parser.add_argument('-l', '--link', type=str, required=True, help='Youtube Playlist/Track link.')
	parser.add_argument('-o', '--output', type=str, default=OUTPUT_DIR, help='Specify an output directory name.')
	args=parser.parse_args()

	# Create the output directory
	os.makedirs(args.output, exist_ok=True)
	print(f"Track(s) will be downloaded to: {args.output}")

	# Download
	main(args.link, args.output)