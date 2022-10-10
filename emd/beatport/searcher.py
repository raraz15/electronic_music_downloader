import re
import requests
from bs4 import BeautifulSoup

HOME_PAGE="https://www.beatport.com"

def make_beatport_query(query_str):
    """Returns the top url from a beatport search. query_str should contain
    track title, artist names, mix types etc."""
    
    try:
        # Beatport query works like this
        query_str=re.sub(r"'","%27", query_str)
        query_str=re.sub(r"\[","%5B", query_str)
        query_str=re.sub(r"\]","%5D", query_str)
        query_str=re.sub(r"&","%26", query_str)
        query_str=re.sub(r"\s","+", query_str)
        query_str=re.sub(r",","%2C", query_str)
        # Form the query url
        url=f"{HOME_PAGE}/search?q={query_str}"
        html=requests.get(url).content
        bsObj=BeautifulSoup(html,'lxml')
        t=bsObj.find("li",{"class":"bucket-item ec-item track"}) # List containing the tracks
        track_url=t.find("div",{"class": "buk-track-meta-parent"}).find("a")["href"]
        return HOME_PAGE+"/"+track_url
    except:
        print(f"Error on: {query_str}")
        return ""