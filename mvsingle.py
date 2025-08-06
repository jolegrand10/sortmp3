""" This is Module fn2at.py for FileName To Artist Title
    Infers MP3 tags from the filename without overwriting existing data
"""

import sys
import os
import eyed3
import re
import shutil
from mutagen.mp3 import MP3
from mutagen.id3 import TCON, TPE1, TIT2, ID3


class MoveSingle():



    def __init__(self, infolder='.', outfolder='.'):
        self.infolder = infolder
        self.outfolder = outfolder

    def run(self):
        """ """
        for root, _, files in os.walk(self.infolder):
            for file in files:
                log(f"Processing file: {file}")
                # Only process mp3 files
                if file.endswith('.mp3'):
                    filepath = os.path.join(root, file)
                    filename = os.path.basename(filepath)
                    # Strict regex: artist space hyphen space title.mp3
                    match = re.match(r'^(.+?) - (.+?)\.mp3$', filename)
                    if not match:
                        continue
                    #
                    # load file
                    #
                    audiofile = eyed3.load(filepath)
                    #
                    # check tags
                    #
                    if audiofile.tag is None:
                        log(f"Failed to retrieve tags from {filename=}")
                        continue
                    #
                    # retrieve tags
                    #
                    artist = audiofile.tag.artist
                    if not artist:
                        log(f"Artist missing for {filename=}")
                        continue
                    #
                    #
                    #
                    title = audiofile.tag.title
                    if not title:
                        log(f"Title missing for {filename=}")
                        continue
                    #
                    #
                    #
                    album = audiofile.tag.album
                    if not album:
                        log(f"Album missing for {filename=} will be set to \"Single\"")
                        album="Single"
                    #
                    # create folder path
                    #
                    target_dir = os.path.join(self.outfolder, "Music", artist, album)
                    try:
                        os.makedirs(target_dir, exist_ok=True)
                    except OSError as e:
                        log(f"Cannot create folder path {target_dir=}")
                        log(f"Cause: {e}")
                        continue
                    target_file = os.path.join(target_dir, filename)
                    #
                    # move mp3 file to its final place
                    # 
                    shutil.move(filepath, target_file) 


   

def log(s):
    print(s)


def main():
    infolder = sys.argv[1] if len(sys.argv) > 1 else '.'
    outfolder = sys.argv[2] if len(sys.argv) > 2 else '.'
    log(f"MoveSingle")
    log(f"Input folder: {infolder}")
    log(f"Output folder: {outfolder}")
    app = MoveSingle(infolder, outfolder)
    app.run()


if __name__ == "__main__":
    main()
