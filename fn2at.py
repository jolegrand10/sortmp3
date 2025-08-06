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


class FileNameToArtistTitle():

    DEFAULT_GENRE = "Other"

    def __init__(self, infolder='.', outfolder='.'):
        self.infolder = infolder
        self.outfolder = outfolder

    def run(self):
        """ Update Tags for all mp3 files in the infolder and move them to the outfolder """
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
                    self.artist, self.title = match.group(
                        1).strip(), match.group(2).strip()
                    ret = self.update_tags(filepath)
                    if ret:
                        shutil.move(filepath, os.path.join(
                            self.outfolder, f"{self.artist} - {self.title}.mp3"))

    def update_tags(self, filepath):
        try:
            self.update_tags_eyed3(filepath)
            return True
        except eyed3.id3.GenreException as e:
            log(f"Invalid genre not supported by EyeD3, trying Mutagen")
            try:
                self.update_tags_mutagen(filepath)
                return True
            except Exception as e1:
                log(f"Failed to update tags with Mutagen. Cause: {e1}")
                return False
        except Exception as e:
            log(f"Failed to update tags with EyeD3. Cause: {e}")
            return False

    def update_tags_eyed3(self, filepath):
        """ Use eyed3 to update tags """
        #
        # load file
        #
        audiofile = eyed3.load(filepath)
        #
        # Load will fail if genre has an illegal value
        #
        if audiofile.tag is None:
            audiofile.initTag()
        #
        # Do not overwrite existing tags
        #
        if not audiofile.tag.artist:
            audiofile.tag.artist = self.artist
        if not audiofile.tag.title:
            audiofile.tag.title = self.title
        #
        # save file in place
        #
        audiofile.tag.save()

    def update_tags_mutagen(self, filepath):
        """ Use Mutagen to update tags """
        #
        # Load file
        #
        audiofile = MP3(filepath, ID3=ID3)

        if audiofile.tags is None:
            audiofile.add_tags()

        #
        # Correct genre tag, because if we are here it is because
        # of an illegal value of genre
        #
        audiofile.tags['TCON'] = TCON(encoding=3, text=[ FileNameToArtistTitle.DEFAULT_GENRE])
        log(f"Genre tag updated")
        #
        # Check and add artist tag if missing
        #
        if 'TPE1' not in audiofile.tags:
            audiofile.tags.add(TPE1(encoding=3, text=[self.artist]))
        #
        # Check and add title tag if missing
        if 'TIT2' not in audiofile.tags:
            audiofile.tags.add(TIT2(encoding=3, text=[self.title]))
        #
        # save file in place
        #
        audiofile.save()


def log(s):
    print(s)


def main():
    infolder = sys.argv[1] if len(sys.argv) > 1 else '.'
    outfolder = sys.argv[2] if len(sys.argv) > 2 else '.'
    log(f"FileNameToArtistTitle")
    log(f"Input folder: {infolder}")
    log(f"Output folder: {outfolder}")
    app = FileNameToArtistTitle(infolder, outfolder)
    app.run()


if __name__ == "__main__":
    main()
