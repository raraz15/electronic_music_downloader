#!/usr/bin/env python
# coding: utf-8

import os
#import traceback
import argparse
import datetime as dt

import youtube_dl

OUTPUT_DIR = "Downloads"
DATE=dt.datetime.strftime(dt.datetime.now(),'%d_%m_%y')
SIMPLE_FORMAT=f"%(title)s.%(ext)s"
YDL_OPTS = {
		'format': 'bestaudio/best',
		'postprocessors': [{'key': 'FFmpegExtractAudio',
							'preferredcodec': 'mp3',
							}],
		# 'preferredquality': '320' upsamples!
	}

def main(URL,output_dir):

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
			
	for link in links:
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


# TODO: faster flattening
if __name__ == '__main__':

	parser = argparse.ArgumentParser(description='Youtube mp3 downloader.')
	parser.add_argument('-l', '--link', type=str, required=True, help='Youtube Playlist/Track link.')
	parser.add_argument('-o', '--output', type=str, default='', help='Specify an output directory name.')
	args = parser.parse_args()

	# Determine and create the output directory
	if args.output=='': # Default output Directory
		output_dir=f"{OUTPUT_DIR}/{DATE}"
	else: # If user specified a directory, overwrite the default
		output_dir=args.output
	os.makedirs(output_dir, exist_ok=True)
	print(f"Track(s) will be downloaded to: {output_dir}")

	# Download
	main(args.link, output_dir)