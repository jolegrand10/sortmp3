""" This is Module fn2at.py for FileName To Artist Title
    Infers MP3 tags from the filename without overwriting existing data
"""

import sys
import os
import eyed3
import re

def update_tags_from_filename(filepath):
    filename = os.path.basename(filepath)
    # Strict regex: artist space hyphen space title.mp3
    match = re.match(r'^(.+?) - (.+?)\.mp3$', filename)
    if not match:
        return  # format not matched, do nothing

    artist, title = match.group(1).strip(), match.group(2).strip()

    audiofile = eyed3.load(filepath)
    if audiofile is None:
        print(f"Cannot load file {filepath}")
        return

    if audiofile.tag is None:
        audiofile.initTag()

    # Do not overwrite existing tags
    if not audiofile.tag.artist:
        audiofile.tag.artist = artist
    if not audiofile.tag.title:
        audiofile.tag.title = title

    audiofile.tag.save()

def log(s):
	print(s)

if __name__ == "__main__":
    # iterate over all mp3 files passed as arguments
    for mp3file in sys.argv[1:]:
	    #
	    # Debug
	    #
        log(f"{mp3file=}")
        update_tags_from_filename(mp3file)

