""" test_fix.py - Test for fix.py """
import argparse
from sortmp3.fix import FixMusicFile
import sys
import pytest
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TCON
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from mutagen import File
from pathlib import Path
import shutil

def mk_m4a(filepath, artist="", album="", title="", genre=""):
    """Make an M4A file with no audio """

    # 1. Copy sample.m4a to path
    shutil.copy("tests/sample.m4a", filepath)
    

    # 2. Load it with Mutagen
    audio = MP4(filepath)

    # 3. Add empty tags (all strings set to "")
    audio["\xa9nam"] = [title]  # Title
    audio["\xa9ART"] = [artist]  # Artist
    audio["\xa9alb"] = [album]  # Album
    audio["\xa9gen"] = [genre]  # Genre

    # 4. Save the file back with empty metadata
    audio.save()



def mk_mp3(filepath, artist="", album="", title="", genre=""):
    """ Make an MP3 file with silent audio but just a header """
    #
    # copy sample.mp3 to filepath
    #
    shutil.copy("tests/sample.mp3", filepath)
    # Load it
    audio = MP3(filepath)

    # Add empty tags
    audio["TIT2"] = TIT2(encoding=3, text=title)   # Titre
    audio["TPE1"] = TPE1(encoding=3, text=artist)   # Artiste
    audio["TALB"] = TALB(encoding=3, text=album)   # Album
    audio["TCON"] = TCON(encoding=3, text=genre)   # Genre

    # save
    audio.save()



def test_empty_infolder(tmp_path):
    """ Test the Fix class with an empty input folder"""
    #
    # create temp folders for infolder and outfolder
    #    
    inf = tmp_path / "in"
    inf.mkdir()
    outf = tmp_path / "out"
    outf.mkdir()
    f=FixMusicFile(infolder=inf, outfolder=outf)
    r = f.run()
    assert r==0

def test_1_file_no_tags_no_album(tmp_path):
    """ Test the Fix class with a single music file and no tags
       Music file is located directly in the infolder so there is
       no relevant Album information. Should be defaulted to Single"""
    #
    # create temp folders for infolder and outfolder
    #    
    inf = tmp_path / "in"
    inf.mkdir()
    outf = tmp_path / "out"
    outf.mkdir()
    #
    # create an MP3 file in inf folder wiht no tags
    #
    mk_mp3(inf / "The Beatles - Penny Lane.mp3")
    #
    # run 
    #
    fmf=FixMusicFile(infolder=inf, outfolder=outf, dry_run=False)
    r = fmf.run()
    #
    # check 1 file has been processed
    #
    assert r==1
    #
    # check Music hierarchy contains the mp3 file
    #
    fo = outf / "Music/The Beatles/Single/The Beatles - Penny Lane.mp3"
    assert Path(outf / "Music").exists()
    assert Path(outf / "Music/The Beatles").exists()
    assert Path(outf / "Music/The Beatles/Single").exists()
    assert fo.exists()
    assert fo.is_file()
    #
    # check output file's tags
    #
    audiofile = File(fo, easy=True)  # easy=True for a unified dict-like interface
    assert audiofile is not None
    assert audiofile.get("artist", [""])[0] == "The Beatles"
    assert audiofile.get("title", [""])[0] == "Penny Lane"
    assert audiofile.get("album", [""])[0] == "Single"


def test_1_file_no_tags_with_album(tmp_path):
    """ Test the Fix class with a single music file and no tags
       Music file is located in a folder named after the album name in the infolder. 
       Relevant album name should be taken"""
    #
    # create temp folders for infolder and outfolder
    #    
    inf = tmp_path / "in"
    inf.mkdir()
    outf = tmp_path / "out" 
    outf.mkdir()
    albumf = inf / "Magical Mystery Tour"
    albumf.mkdir()
    #
    # create an MP3 file in inf folder wiht no tags
    #
    mk_mp3(albumf / "The Beatles - Penny Lane.mp3")
    #
    # run 
    #
    fmf=FixMusicFile(infolder=inf, outfolder=outf, dry_run=False)
    r = fmf.run()
    #
    # check 1 file has been processed
    #
    assert r==1
    #
    # check Music hierarchy contains the mp3 file
    #
    fo = outf / "Music/The Beatles/Magical Mystery Tour/The Beatles - Penny Lane.mp3"
    assert Path(outf / "Music").exists()
    assert Path(outf / "Music/The Beatles").exists()
    assert Path(outf / "Music/The Beatles/Magical Mystery Tour").exists()
    assert fo.exists()
    assert fo.is_file()
    #
    # check output file's tags
    #
    audiofile = File(fo, easy=True)  # easy=True for a unified dict-like interface
    assert audiofile is not None
    assert audiofile.get("artist", [""])[0] == "The Beatles"
    assert audiofile.get("title", [""])[0] == "Penny Lane"
    assert audiofile.get("album", [""])[0] == "Magical Mystery Tour"


def test_collisions_no_overwrite(tmp_path):
    """ infolder/subfolder1/album_a/artist_a - title_a.mp3
    and
        infolder/subfolder2/album_a/artist_a - title_a.mp3
        
    creates the condition for a collision in Music Hierarchy"""
    #
    # create temp folders for infolder and outfolder
    #    
    inf = tmp_path / "in"
    inf.mkdir()
    outf = tmp_path / "out" 
    outf.mkdir()
    subfolder1 = inf / "Subfolder1"
    subfolder1.mkdir()
    albumf1 = subfolder1 / "Magical Mystery Tour"
    albumf1.mkdir()
    #
    # create an MP3 file in inf folder wiht no tags
    #
    mk_mp3(albumf1 / "The Beatles - Penny Lane.mp3")
    #
    # create duplicate
    #
    subfolder2 = inf / "Subfolder2"
    subfolder2.mkdir()
    albumf2 = subfolder2 / "Magical Mystery Tour"
    albumf2.mkdir()
    #
    # create an MP3 file in inf folder wiht no tags
    #
    mk_mp3(albumf2 / "The Beatles - Penny Lane.mp3")
    #
    # run 
    #
    fmf=FixMusicFile(infolder=inf, outfolder=outf, dry_run=False, overwrite=False)
    r = fmf.run()
    #
    # check 2 files have been processed
    #
    assert r==2
    #
    # check Music hierarchy contains the mp3 file
    #
    fo = outf / "Music/The Beatles/Magical Mystery Tour/The Beatles - Penny Lane.mp3"
    assert Path(outf / "Music").exists()
    assert Path(outf / "Music/The Beatles").exists()
    assert Path(outf / "Music/The Beatles/Magical Mystery Tour").exists()
    assert fo.exists()
    assert fo.is_file()
    #
    # check that duplicate remains in infolder
    # 1 of the 2 but not the 2 together
    #
    assert (bool(Path(albumf1 / "The Beatles - Penny Lane.mp3").exists())^ 
        bool(Path(albumf2 / "The Beatles - Penny Lane.mp3").exists()))


def test_collisions_with_overwrite(tmp_path):
    """ infolder/subfolder1/album_a/artist_a - title_a.mp3
    and
        infolder/subfolder2/album_a/artist_a - title_a.mp3
        
    creates the condition for a collision in Music Hierarchy"""
    #
    # create temp folders for infolder and outfolder
    #    
    inf = tmp_path / "in"
    inf.mkdir()
    outf = tmp_path / "out" 
    outf.mkdir()
    subfolder1 = inf / "Subfolder1"
    subfolder1.mkdir()
    albumf1 = subfolder1 / "Magical Mystery Tour"
    albumf1.mkdir()
    #
    # create an MP3 file in inf folder wiht no tags
    #
    mk_mp3(albumf1 / "The Beatles - Penny Lane.mp3")
    #
    # create duplicate
    #
    subfolder2 = inf / "Subfolder2"
    subfolder2.mkdir()
    albumf2 = subfolder2 / "Magical Mystery Tour"
    albumf2.mkdir()
    #
    # create an MP3 file in inf folder wiht no tags
    #
    mk_mp3(albumf2 / "The Beatles - Penny Lane.mp3")
    #
    # run 
    #
    fmf=FixMusicFile(infolder=inf, outfolder=outf, dry_run=False, overwrite=True)
    r = fmf.run()
    #
    # check 2 files have been processed
    #
    assert r==2
    #
    # check Music hierarchy contains the mp3 file
    #
    fo = outf / "Music/The Beatles/Magical Mystery Tour/The Beatles - Penny Lane.mp3"
    assert Path(outf / "Music").exists()
    assert Path(outf / "Music/The Beatles").exists()
    assert Path(outf / "Music/The Beatles/Magical Mystery Tour").exists()
    assert fo.exists()
    assert fo.is_file()
    #
    # check that duplicate is no longer in infolder
    # 
    #
    assert not (bool(Path(albumf1 / "The Beatles - Penny Lane.mp3").exists()) and not
        bool(Path(albumf2 / "The Beatles - Penny Lane.mp3").exists()))

    

def test_single_file(monkeypatch):
    """ Test the Fix class with a single music file and  tags"""
    pass

def test_album(monkeypatch):
    """ Test the Fix class with a single music file and no tags"""
    pass
