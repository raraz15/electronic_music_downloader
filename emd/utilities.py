import re
import unicodedata

def key_formatter(key):
    key=re.sub(r'\u266f', "b", key)
    key=re.sub(r'\u266d', "#", key)
    scale_type=key[-3:]
    root=key.split(scale_type)[0]
    if ' ' in root:
        root=root[:root.index(' ')]
    root=sharpen_flats(root)
    if root == 'B#':
        root='C'
    if root == 'E#':
        root='F' 
    key='{} {}'.format(root, scale_type.lower())
    return key

def sharpen_flats(root):
    roots=['C','D','E','F','G','A','B'] 
    if 'b' in root:
        natural_harmonic=root[:1]
        idx=roots.index(natural_harmonic)
        sharpened_root=roots[idx-1]
        root="{}#".format(sharpened_root)
    return root

def replace_non_ascii(str):
    str=unicodedata.normalize('NFKD', str).encode('ascii', 'ignore')
    str=str.decode("utf-8") # For json dump
    return str

def make_name(name_dict_list):
    name=", ".join([artist["name"] for artist in name_dict_list])
    name=replace_non_ascii(name)
    return name

# TODO: Utils.py maybe
def duration_str_to_int(duration_str):
    min,sec=duration_str.split(":")
    duration=int(sec)+60*int(min)
    return duration

def format_key(key):
    min_maj=key[-3:]
    natural_harmonic=key.split(min_maj)[0]
    return natural_harmonic+" "+min_maj

def format_genre_string(genre):
    genre=re.sub(r"\s/\s","-",genre)
    genre=re.sub(r"\s&\s","&",genre)
    genre=re.sub(r"\s","_",genre)
    return genre

