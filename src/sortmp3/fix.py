""" This is Module fixmusfil.py for Fix Music FIle
    Fixes the location of a file by moving it to its right place in the Music hierarchy
    Based on info found in the file path Artist-Title.mp3
"""

import sys
import os
from pathlib import Path
import logging
from mutagen import File
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3NoHeaderError
import re
import shutil


def dir_empty(dir_path):
    """ the fastest way to check if dir_path is empty """
    return not next(os.scandir(dir_path), None)


def dir_empty(dir_path):
    """ pathlib version """
    return dir_path.is_dir() and not any(dir_path.iterdir())


def clean_dirs(root: Path) -> int:
    """
    Supprime tous les dossiers vides de manière récursive.
    Retourne le nombre de dossiers supprimés.
    """
    removed = 0
    # loop on subfolders
    for child in list(root.iterdir()):
        print(f"Checkin child {child}")
        #
        # clean child folders' content first
        #
        if child.is_dir():
            print(f"{child} is dir")
            if dir_empty(child):
                child.rmdir()
                removed += 1
            else:
                removed += clean_dirs(child)
            #
            # clean child itself
            #
            if dir_empty(child):
                child.rmdir()
                removed += 1
    return removed


class FixMusicFile():

    ITEMS = "artist album title".split()

    def __init__(self, infolder='.', outfolder='.', errfolder=None,
                 artist="Tag", album="Tag", title="Tag",
                 dry_run=True, overwrite=False):

        # a bunch of files and folders among them music files in mp3 or m4a format
        self.infolder = Path(infolder).expanduser().resolve()

        # a place where the Music Hierarchy lives
        self.outfolder = Path(outfolder).expanduser().resolve()

        # a place to store files that are rejected for some reason
        self.errfolder = infolder if errfolder is None else Path(
            errfolder).expanduser().resolve()

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
            return normalize_spaces(re.sub(r'[<>:"/\\|?*\x00-\x1F]', ' ', s)[:255])


        def normalize_spaces(text):
            """ substitutes multiple space chars by one char.
                eliminates leading and trailng spaces"""
            text = re.sub(r'\s+', ' ', text)
            return text.strip()

        n = 0
        logging.info(f"Starting exploring music files in {self.infolder}")
        initial_folder_name = self.infolder.name
        logging.debug(f"{initial_folder_name=}")
        #
        # To allow inplace processing when infolder and outfolder are the same
        #
        files = list(self.infolder.rglob("*"))
        #
        # retain files only
        #
        files = [f for f in files if f.is_file()]
        for file in files:
                # Strict regex: artist space hyphen space title.mp3 or m4a
                match = re.match(r'^(.+?) - (.+?)\.(mp3|m4a)$', file.name)
                if not match:
                    continue
                logging.debug(f"Processing {file.name}")
                n += 1
                #
                # collect info from file system
                #
                fil_ = {}
                fil_["artist"] = match.group(1).strip().title()
                fil_["title"] = match.group(2).strip().title()
                filtyp = match.group(3).strip().lower()
                # get last folder and beware of trailing slashes
                fil_["album"] = file.parent.name
                if initial_folder_name == fil_["album"]:
                    fil_["album"] = ""
                temp = " * ".join([fil_[it] for it in FixMusicFile.ITEMS])
                logging.debug(f"File info: {temp}")
                #
                # collect info from tags
                #
                try:
                    # easy=True for a unified dict-like interface
                    audiofile = File(file, easy=True)                    
                    assert filtyp=="mp3" and isinstance(audiofile, EasyID3), "mp3 audiofile is not an EasyID3"
                except (AssertionError, ID3NoHeaderError) :
                    audiofile = EasyID3()
                    audiofile.save(file)
                    audiofile = EasyID3(file)

                if audiofile is None:
                    raise ValueError(f"Unsupported file type: {file}")
                #
                # Some tags may be missing, so we use .get(key, [""])[0]
                tag_ = {}
                for it in FixMusicFile.ITEMS:
                    tag_[it] = sanitize(audiofile.get(it, [""])[0])
                temp = " * ".join([tag_[it] for it in FixMusicFile.ITEMS])
                logging.debug(f"Original tags: {temp}")
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
                #
                target_dir = Path(self.outfolder, "Music", sanitize(
                    audiofile["artist"][0]), sanitize(audiofile["album"][0]))
                try:
                    target_dir.mkdir(parents=True, exist_ok=True)
                except OSError as e:
                    logging.error(f"Cannot create folder path {target_dir=}")
                    logging.error(f"Cause: {e}")
                    continue
                #
                # create filename
                #
                filename = audiofile["artist"][0] + " - " + \
                    audiofile["title"][0] + "." + filtyp
                target_file = target_dir / sanitize(filename)
                logging.info(f"Moving to {target_file.name}")
                #
                # move mp3 file to its final place
                #
                if not self.dry_run:
                    if target_file.exists() and target_file.is_file() and not self.overwrite:
                        logging.warning(f"Duplicate ignored: {target_file.name}")
                    else:
                        shutil.move(file, target_file)
        p = 0 if self.dry_run else clean_dirs(self.infolder)
        logging.info(f"Files processed: {n}")
        if p:
            logging.info(f"Folders cleaned: {p}")
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


def test():
    clean_dirs(Path(r'C:\Users\Georges Georgoulis\desktop\temp'))


if __name__ == "__main__":
    test()
