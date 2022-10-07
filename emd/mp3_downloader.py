import os
import re
import shutil
import argparse
import datetime as dt

import youtube_dl
from mutagen.id3 import ID3, TPE1, TIT2

from info import TRACKS_DIR # Default dir

DATE=dt.datetime.strftime(dt.datetime.now(),'%d_%m_%y')
OUTPUT_DIR=os.path.join(TRACKS_DIR,DATE)

SIMPLE_FORMAT=f"%(title)s.%(ext)s"
YDL_OPTS={
		'format': 'bestaudio/best',
		'postprocessors': [{'key': 'FFmpegExtractAudio',
							'preferredcodec': 'mp3',
							}],
		# 'preferredquality': '320' upsamples, not real 320kbps
	}

def clean_file_name(title,output_dir):
	clean_title=re.sub(r"\s\s+"," ",title)      # Multiple
	clean_title=re.sub(r"\A\s+","",clean_title) # Leading 
	clean_title=re.sub(r"\s+\Z","",clean_title) # Trailing
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

def flatten_playlist(url):
	"""If the url is of a playlist, it flattens it."""
	urls=[]
	with youtube_dl.YoutubeDL(YDL_OPTS) as ydl: # Get all the individual urls
		result=ydl.extract_info(url, download=False)
		if 'entries' in result: # Playlist
			for i,_ in enumerate(result['entries']):
				urls.append(result['entries'][i]['webpage_url'])
			print("Flattened the playlist.")
		else:
			urls=[url] # Single track
	return urls

def set_id3_tag(audio_path,id3_tag):
	print("Setting the id3 tag...")
	artist,title=id3_tag
	audio=ID3(audio_path)
	audio['TPE1']=TPE1(encoding=3,text=artist)
	audio['TIT2']=TIT2(encoding=3,text=title)
	audio.save(v2_version=3)

def download_single_track(url,output_dir,clean=False,id3_tag=None):
	attempt=False
	with youtube_dl.YoutubeDL(YDL_OPTS) as ydl:
		# Get information to determine name formatting
		info_dict=ydl.extract_info(url,download=False)
		# Check the audio sampling rate
		if int(info_dict.get('asr', None))<44100:
			attempt=True
			print("Low sampling rate! Skipping.")
		else:
			artist=info_dict.get('artist',None)
			track=info_dict.get('track',None)
			# Change the formatting if artist and track name is specified
			if (artist is not None) and (track is not None):
				form="%(artist)s - %(track)s.%(ext)s"
				YDL_OPTS['outtmpl']=f"{output_dir}/{form}"
				title=f"{artist} - {track}"
				id3_tag=(artist,track)
			else: # Attempt download with the current format
				attempt=True
				title=info_dict.get('title', None)
				try:
					ydl.download([url])
					if id3_tag is not None: # Set the id3tag if provided
						mp3_path=os.path.join(output_dir,f"{title}.mp3")
						set_id3_tag(mp3_path,id3_tag)
					if clean: # Clean the file name
						clean_file_name(title,output_dir)
				except Exception:
					print(f"There was an error on: {url}")
				print("")
	if not attempt:
		# Set the new format and Download
		with youtube_dl.YoutubeDL(YDL_OPTS) as ydl:
			try:
				ydl.download([url])
				if id3_tag is not None: # Set the id3tag if provided
					mp3_path=os.path.join(output_dir,f"{title}.mp3")
					set_id3_tag(mp3_path,id3_tag)
				if clean: # Clean the file name
					clean_file_name(title,output_dir)
			except Exception:
				print(f"There was an error on: {url}")

def main(url,output_dir,verbose=True,clean=False):
	"""Downloads the youtube mp3/mp3s to output_dir with metadata, id3 tag formatting."""

	# Initialize the output format
	YDL_OPTS['outtmpl']=f"{output_dir}/{SIMPLE_FORMAT}"
	# Flatten the urls if its a playlist
	urls=flatten_playlist(url)
	if verbose:
		print("Starting to download...\n")
	for i,url in enumerate(urls):
		if verbose:
			print(f"{i+1}/{len(urls)}")
		download_single_track(url,output_dir,clean)
		# Go back to the default format
		YDL_OPTS['outtmpl']=f"{output_dir}/{SIMPLE_FORMAT}"
		print("")

# TODO: change the name to download_mp3
# TODO: faster flattening
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