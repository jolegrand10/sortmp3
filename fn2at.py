""" This is Module fn2at.py for FileName To Artist Title
    Infers MP3 tags from the filename without overwriting existing data
"""

import sys
import os
import eyed3
import re
import shutil

class FileNameToArtistTitle():
    def __init__(self, infolder='.', outfolder='.'):
        self.infolder = infolder
        self.outfolder = outfolder

    def run(self):
        for root, _, files in os.walk(self.infolder):
            for file in files:
                log(f"Processing file: {file}")
                # Only process mp3 files  
                if file.endswith('.mp3'):
                    filepath = os.path.join(root, file)
                    self.update_tags_from_filename(filepath)
    
    def update_tags_from_filename(self, filepath):
        filename = os.path.basename(filepath)
        # Strict regex: artist space hyphen space title.mp3
        match = re.match(r'^(.+?) - (.+?)\.mp3$', filename)
        if not match:
            return  # format not matched, do nothing

        artist, title = match.group(1).strip(), match.group(2).strip()

        try:
            audiofile = eyed3.load(filepath)
        except Exception as e:
            log(f"Error loading file {filepath}: {e}")
            audiofile = None
        
        if audiofile is None:
            log(f"Cannot load file {filepath}")
            return

        if audiofile.tag is None:
            audiofile.initTag()

        # Do not overwrite existing tags
        if not audiofile.tag.artist:
            audiofile.tag.artist = artist
        if not audiofile.tag.title:
            audiofile.tag.title = title

        audiofile.tag.save()
        shutil.move(filepath, os.path.join(self.outfolder, f"{artist} - {title}.mp3"))


def log(s):
	print(s)


def main():
    infolder= sys.argv[1] if len(sys.argv) > 1 else '.'
    outfolder = sys.argv[2] if len(sys.argv) > 2 else '.'
    log(f"FileNameToArtistTitle")
    log(f"Input folder: {infolder}")
    log(f"Output folder: {outfolder}")
    app = FileNameToArtistTitle(infolder, outfolder)
    app.run()


if __name__ == "__main__":
    main()

