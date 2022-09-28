#!/usr/bin/env python
# coding: utf-8

import os,sys
import traceback
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

# TODO: raise warning if quality not 320
# TODO: faster flattening
if __name__ == '__main__':

	parser = argparse.ArgumentParser(description='Youtube mp3 downloader.')
	parser.add_argument('-l', '--link', type=str, required=True, help='Youtube Playlist/Track link.')
	parser.add_argument('-o', '--output', type=str, default='', help='Specify an output directory name.')
	parser.add_argument('-v', '--verbose', action='store_true', help='Control printing.')
	args = parser.parse_args()

	# If user specified a directory, overwrite the default
	if args.output!='': 
		OUTPUT_DIR=args.output
	else:
		OUTPUT_DIR=f"{OUTPUT_DIR}/{DATE}"
	YDL_OPTS['outtmpl']=f"{OUTPUT_DIR}/{SIMPLE_FORMAT}"
	# Create the Output Directory
	os.makedirs(OUTPUT_DIR, exist_ok=True)
	if args.verbose:
		print(f"Track(s) will be downloaded to: {OUTPUT_DIR}")

	# Flatten the links if its a playlist
	links=[]
	with youtube_dl.YoutubeDL(YDL_OPTS) as ydl: # Get all the individual links
		result=ydl.extract_info(args.link, download=False)
		if 'entries' in result: # Playlist
			for i,item in enumerate(result['entries']):
				links.append(result['entries'][i]['webpage_url'])
			print("Flattened the playlist.")
		else:
			links=[args.link] # Single track
			
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
				YDL_OPTS['outtmpl']=f"{OUTPUT_DIR}/{form}"
			else: # Attempt download with the current format
				try:
					ydl.download([link])
				except KeyboardInterrupt:
					sys.exit(1)				
				except Exception as ex:     
					print(f"There was an error on: {link}")
					exception_str = ''.join(traceback.format_exception(etype=type(ex), value=ex, tb=ex.__traceback__))
					print(exception_str)
				print("")
				continue
		# Set the new format and Download
		with youtube_dl.YoutubeDL(YDL_OPTS) as ydl:
			try:
				ydl.download([link])
			except KeyboardInterrupt:
				sys.exit(1)				
			except Exception as ex:     
				print(f"There was an error on: {link}")
				exception_str = ''.join(traceback.format_exception(etype=type(ex), value=ex, tb=ex.__traceback__))
				print(exception_str)
		# Go back to the default format
		YDL_OPTS['outtmpl']=f"{OUTPUT_DIR}/{SIMPLE_FORMAT}"
		print("")