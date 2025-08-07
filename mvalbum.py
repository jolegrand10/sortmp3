""" This is Module mvalbum.py.py for MoveAlbum
    Introduces the Album in the music hierarchy
"""

import sys
import os
import eyed3
import re
import shutil
from mutagen.mp3 import MP3
from mutagen.id3 import TCON, TPE1, TIT2, ID3
from pathlib import Path


class MoveAlbum():
    """ Moves albums in the music hierarchy"""

    def __init__(self, infolder='.', outfolder='.'):
        self.infolder = Path(infolder)
        self.outfolder = outfolder

    def run(self):
        """ Moves the music files contained in an album folder to the right place in the music hierarchy """
        pattern = re.compile(r"^(.*?)\s-\s(.*?)$")
        for folder in self.infolder.iterdir():
            if folder.is_dir():
                log(f"Processing {folder.name}")
                # Analyze the folder name - to recognize Artist - Album pattern
                pattern = re.compile(r"^(.*?)\s-\s(.*?)$")
                match = pattern.match(folder.name)
                if match:
                    artist, album = match.groups()
                    artist = artist.strip()
                    album = album.strip()
                    #
                    # create folder path
                    #
                    target_dir = os.path.join(self.outfolder, "Music", artist, album)
                    #
                    # ensure target-dir exists
                    #
                    try:
                        os.makedirs(target_dir, exist_ok=True)
                    except OSError as e:
                        log(f"Cannot create folder path {target_dir=}")
                        log(f"Cause: {e}")
                        continue
                    #
                    # copy the album files one by one and check for collisions
                    #
                    for file in folder.iterdir():
                        if file.is_file():
                            destination_file = Path(target_dir) / file.name
                            if destination_file.exists():
                                log(f"Duplicate file found: {destination_file}")
                            else:
                                #
                                #
                                #
                                shutil.move(file, destination_file)
                    #
                    # if the album dir is empty, erase it !
                    #
                    if not any(folder.iterdir()):  # True if empty
                        folder.rmdir()  # remove the empty folder


   

def log(s):
    print(s)


def main():
    infolder = sys.argv[1] if len(sys.argv) > 1 else '.'
    outfolder = sys.argv[2] if len(sys.argv) > 2 else '.'
    log(f"MoveAlbum")
    log(f"Input folder: {infolder}")
    log(f"Output folder: {outfolder}")
    app = MoveAlbum(infolder, outfolder)
    app.run()


if __name__ == "__main__":
    main()
