""" This is Module fixmusfil.py for Fix Music FIle
    Fixes the location of a file by moving it to its right place in the Music hierarchy
    Based on info found in the file path Artist-Title.mp3
"""

import sys
import os
import logging
from mutagen import File
import re
import shutil


class FixMusicFile():

    ITEMS = "artist album title".split()

    def __init__(self, infolder='.', outfolder='.', errfolder=None,
                 artist="Tag", album="Tag", title="Tag",
                 dry_run=True, overwrite=False):

        # a bunch of files and folders among them music files in mp3 or m4a format
        self.infolder = infolder

        # a place where the Music Hierarchy lives
        self.outfolder = outfolder

        # a place to store files that are rejected for some reason
        self.errfolder = infolder if errfolder is None else errfolder

        # priority to file info or tag info
        self.priority = {}
        self.priority["artist"] = artist
        self.priority["album"] = album
        self.priority["title"] = title

        self.dry_run = dry_run
        self.overwrite = overwrite

    def __repr__(self):
        attrs = ", ".join(f"{k}={v!r}" for k, v in vars(self).items())
        return f"{self.__class__.__name__}({attrs})"

    def run(self):
        """ 
            Music Tags are modified depending on available info and priority

            File / Tag    Absent  Present 
            Absent          ...     ...         File info is always present
            Present         File    Priority

            Filenames reflect Music Tags when file is put in its place in the Music Hierarchy
            with Artist - Title.mp3 or m4a syntax

        """
        def sanitize(s):
            """ Replaces illegal (windows, POSIX) chars in filenames with _"""
            return (re.sub(r'[<>:"/\\|?*\x00-\x1F]', ' ', s)[:255]).strip()

        n = 0
        logging.info(f"Starting exploring music files in {self.infolder}")
        initial_folder_name = os.path.basename(os.path.normpath(self.infolder))
        logging.debug(f"{initial_folder_name=}")
        for root, _, files in os.walk(self.infolder):
            for file in files:
                filepath = os.path.join(root, file)
                filename = os.path.basename(filepath)
                # Strict regex: artist space hyphen space title.mp3 or m4a
                match = re.match(r'^(.+?) - (.+?)\.(mp3|m4a)$', filename)
                if not match:
                    continue
                logging.debug(f"Processing {filepath}")
                n += 1
                #
                # collect info from file system
                #
                fil_ = {}
                fil_["artist"] = match.group(1).strip().title()
                fil_["title"] = match.group(2).strip().title()
                # filtyp = match.group(3).strip().lower()
                # get last folder and beware of trailing slashes
                fil_["album"] = os.path.basename(os.path.normpath(root))
                if initial_folder_name == fil_["album"]:
                    fil_["album"] = ""
                temp = " * ".join([fil_[it] for it in FixMusicFile.ITEMS])
                logging.debug(f"File info: {temp}")
                #
                # collect info from tags
                #
                # easy=True for a unified dict-like interface
                audiofile = File(filepath, easy=True)
                if audiofile is None:
                    raise ValueError(f"Unsupported file type: {filepath}")
                # Some tags may be missing, so we use .get(key, [""])[0]
                tag_ = {}
                for it in FixMusicFile.ITEMS:
                    tag_[it] = sanitize(audiofile.get(it, [""])[0])
                temp = " * ".join([tag_[it] for it in FixMusicFile.ITEMS])
                logging.debug(f"Original tags: {temp}")
                #
                # merge fil and tag info into new tags consistently with priorities
                #
                # album
                #
                if self.priority["album"] == "File":
                    audiofile["album"] = fil_[
                        "album"] or tag_["album"] or "Single"
                else:
                    audiofile["album"] = tag_[
                        "album"] or fil_["album"] or "Single"
                #
                # artist
                #
                if self.priority["artist"] == "File":
                    audiofile["artist"] = fil_["artist"] or tag_[
                        "artist"] or "Unknown artist"
                else:
                    audiofile["artist"] = tag_["artist"] or fil_[
                        "artist"] or "Unknown artist"
                #
                # title
                #
                if self.priority["title"] == "File":
                    audiofile["title"] = fil_["title"] or tag_[
                        "title"] or "Unknown title"
                else:
                    audiofile["title"] = tag_["title"] or fil_[
                        "title"] or "Unknown title"
                #
                # Note that Tags are modified inplace before file is moved
                #
                temp = " * ".join([audiofile.get(it, ["***"])[0]
                                  for it in FixMusicFile.ITEMS])
                logging.debug(f"Modified tags: {temp}")
                if not self.dry_run:
                    audiofile.save()
                #
                # create folder path
                #
                logging.debug(f'{self.outfolder=}')
                logging.debug(f'{audiofile["artist"]=}')
                logging.debug(f'{audiofile["album"]=}')
                target_dir = os.path.join(self.outfolder, "Music", sanitize(
                    audiofile["artist"][0]), sanitize(audiofile["album"][0]))
                try:
                    os.makedirs(target_dir, exist_ok=True)
                except OSError as e:
                    logging.error(f"Cannot create folder path {target_dir=}")
                    logging.error(f"Cause: {e}")
                    continue
                target_file = os.path.join(target_dir, sanitize(filename))
                logging.info(f"Moving to {target_file=}")
                print(target_file)
                #
                # move mp3 file to its final place
                #
                if not self.dry_run:
                    if os.path.exists(target_file) and os.path.isfile(target_file) and not self.overwrite:
                        logging.warning(f"Duplicate ignored: {target_file}")
                    else:
                        shutil.move(filepath, target_file)
        logging.info(f"Files processed: {n}")
        return n


def main():
    from src.sortmp3.fullog import Full_Log
    Full_Log("FixMusicFile", debug=True, verbose=False,)
    infolder = sys.argv[1] if len(sys.argv) > 1 else '.'
    outfolder = sys.argv[2] if len(sys.argv) > 2 else '.'
    logging.info(f"FixMusicFile")
    logging.info(f"Input folder: {infolder}")
    logging.info(f"Output folder: {outfolder}")
    app = FixMusicFile(infolder, outfolder, dry_run=True)
    logging.info(repr(app))
    app.run()


if __name__ == "__main__":
    main()
