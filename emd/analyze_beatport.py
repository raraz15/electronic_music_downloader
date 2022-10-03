#!/usr/bin/env python
# coding: utf-8

import os
import json
import argparse
from collections import defaultdict

import matplotlib.pyplot as plt

from info import CHARTS_DIR # Default directory

def analyze_and_plot(tracks,save_figure,output_dir,chart_name):

    # Analysis
    key_dict,bpm_dict,label_dict,artist_dict=defaultdict(int),defaultdict(int),defaultdict(int),defaultdict(int)
    remix_dict={'remix': 0, 'original': 0}
    for track in tracks.values():
        bpm_dict[track['BPM']] += 1
        key_dict[track['Key']] += 1
        label_dict[track['Label']] += 1
        for artist in track['Artist(s)'].split(','):
            artist_dict[artist.replace("$$","\$\$")] += 1  # One artist' name included $$ which was bad for OS           
        if track['Remixer(s)']!="":
            remix_dict['remix'] += 1
        else:
            remix_dict['original'] += 1
    artist_dict=dict(sorted(artist_dict.items()))
    key_dict=dict(sorted(key_dict.items()))
    bpm_dict=dict(sorted(bpm_dict.items()))
    label_dict=dict(sorted(label_dict.items())) 

    # Plotting
    genre=chart_name.split("-")[0].replace('_',' ')
    # Pie chart, where the slices will be ordered and plotted counter-clockwise:
    labels=['Remix', 'Original']
    explode=(0, 0.05)  
    fig0, ax=plt.subplots(figsize=(10,5))
    ax.pie(remix_dict.values(), explode=explode, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90, textprops={'fontsize': 15})
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    ax.set_title(f"Beatport {genre} Top100 Remix Distribution",fontsize=14)
    if not save_figure:
        plt.draw()   

    
    artist_counts=list(artist_dict.values())
    artist_names=list(artist_dict.keys())
    good_artist_indices=[i for i,val in enumerate(artist_counts) if val>1]
    artist_counts=[count for i,count in enumerate(artist_counts) if i in good_artist_indices]
    artist_names=[name for i,name in enumerate(artist_names) if i in good_artist_indices]
    fig1, ax=plt.subplots(figsize=(20,8))
    ax.bar(artist_names,artist_counts)
    ax.set_ylabel('Number of Appearances',fontsize=15)
    ax.set_xlabel('Artist',fontsize=15)
    ax.set_title(f"Beatport {genre} Top100 Artist Distribution",fontsize=14)
    plt.xticks(rotation=30)
    if not save_figure:
        plt.draw()    

    fig2, ax=plt.subplots(figsize=(20,8))
    ax.bar(key_dict.keys(), key_dict.values())
    ax.set_ylabel('Number of Tracks',fontsize=15)
    ax.set_xlabel('Track Key',fontsize=15)
    ax.set_title(f"Beatport {genre} Top100 Key Distribution",fontsize=14)
    if not save_figure:
        plt.draw()  

    fig3, ax=plt.subplots(figsize=(20,8))
    ax.bar(bpm_dict.keys(), bpm_dict.values())
    ax.set_ylabel('Number of Tracks',fontsize=15)
    ax.set_xlabel('Track BPM',fontsize=15)
    ax.set_title(f"Beatport {genre} Top100 BPM Distribution",fontsize=14)
    if not save_figure:
        plt.draw()   

    fig4, ax=plt.subplots(figsize=(20,8))
    ax.bar(label_dict.keys(), label_dict.values())
    ax.set_ylabel('Number of Tracks',fontsize=15)
    ax.set_xlabel('Label Name',fontsize=15)
    ax.set_title(f"Beatport {genre} Top100 Label Distribution",fontsize=14)
    plt.xticks(rotation=90)
    if not save_figure:
        plt.draw()
        plt.show()
    else:
        fig0.savefig(os.path.join(output_dir, f"{chart_name}-Remix_Distribution.png"))
        fig1.savefig(os.path.join(output_dir, f"{chart_name}-Artist_Distribution.png"))
        fig2.savefig(os.path.join(output_dir, f"{chart_name}-Key_Distribution.png"))
        fig3.savefig(os.path.join(output_dir, f"{chart_name}-BPM_Distribution.png"))
        fig4.savefig(os.path.join(output_dir, f"{chart_name}-Label_Distribution.png"))
        plt.close("all")

if __name__ == '__main__':

    parser=argparse.ArgumentParser(description='Beatport Top100 Analyzer')
    parser.add_argument('-p', '--path', type=str, required=True, help='Path to the chart_dict.json file.')
    parser.add_argument('-o', '--output', type=str, default='', help='Specify an output directory.')
    parser.add_argument('-s', '--save-figure', action='store_true', help='Save the figures.')
    args=parser.parse_args()

    # Load the chart file
    chart_path=args.path
    if not os.path.isfile(chart_path): # if just the name of the json file is given
        chart_path=os.path.join(CHARTS_DIR, chart_path)
    with open(chart_path, 'r') as infile:
        chart=json.load(infile)
    print("Loaded the chart.")

    # Determine the export directory
    output_path=args.output
    if not os.path.isdir(output_path):
        output_path=os.path.dirname(chart_path)
    print(f"Saving the plots to: {output_path}")

    # Get the name of the chart
    chart_name=os.path.splitext(os.path.basename(chart_path))[0]

    # Analyze and plot
    analyze_and_plot(chart,args.save_figure,output_path,chart_name)
    print("Done!")