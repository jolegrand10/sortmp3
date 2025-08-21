""" test_fix.py - Test for fix.py """
import argparse
from sortmp3.fix import FixMusicFile, dir_empty, clean_dirs
import sys
import pytest
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TCON
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from mutagen import File
from pathlib import Path
import shutil


def test_dir_empty(tmp_path):
    #
    # make an empty dir
    #
    f = tmp_path
    assert dir_empty(f)

def test_clean_dirs(tmp_path):
    #
    # create infolder
    #
    infolder = tmp_path
    #
    # create a long dir branch inside
    #
    sf = infolder
    for i in range(3):
        sf = sf / ("a"+str(i))
        sf.mkdir()
    #
    # check  emptyness before cleaning
    #
    assert dir_empty(sf)
    p=clean_dirs(infolder)
    assert dir_empty(infolder)
    assert p==3



def mk_m4a(filepath, artist="", album="", title="", genre=""):
    """Make an M4A file with no audio """

    # Copy sample.m4a to path
    shutil.copy("tests/sample.m4a", filepath)
    

    # Load it with Mutagen
    audio = MP4(filepath)

    # Add empty tags (all strings set to "")
    audio["\xa9nam"] = [title]  # Title
    audio["\xa9ART"] = [artist]  # Artist
    audio["\xa9alb"] = [album]  # Album
    audio["\xa9gen"] = [genre]  # Genre

    # Save the file back with empty metadata
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
    inf.mkdir(parents=True, exist_ok=True)
    outf = tmp_path / "out"
    outf.mkdir(parents=True, exist_ok=True)
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
    inf.mkdir(parents=True, exist_ok=True)
    assert inf.exists() and inf.is_dir()
    outf = tmp_path / "out"
    outf.mkdir(parents=True, exist_ok=True)
    assert outf.exists() and outf.is_dir()
    #
    # create an MP3 file in inf folder wiht no tags
    #
    mk_mp3(inf / "The Beatles - Penny Lane.mp3")
    assert (inf / "The Beatles - Penny Lane.mp3").exists()
    #
    # run 
    #
    fmf = FixMusicFile(infolder=inf, outfolder=outf, dry_run=False)
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

    

def test_album(tmp_path):
    """ Test the Fix class with an album and several titles """
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
    # create several MP3 files in album folder wiht no tags
    #
    mk_mp3(albumf / "The Beatles - Penny Lane.mp3")
    mk_mp3(albumf / "The Beatles - Hello, Goodbye.mp3")
    mk_mp3(albumf / "The Beatles - Strawberry Fields Forever.mp3")
    #
    # run 
    #
    fmf=FixMusicFile(infolder=inf, outfolder=outf, dry_run=False, overwrite=True)
    r = fmf.run()
    #
    # check 3 files have been processed
    #
    assert r==3
    #
    # check the output - file existence
    #
    fo1 = outf / "Music/The Beatles/Magical Mystery Tour/The Beatles - Penny Lane.mp3"
    assert fo1.exists()
    assert fo1.is_file()
    fo2 = outf / "Music/The Beatles/Magical Mystery Tour/The Beatles - Hello, Goodbye.mp3"
    assert fo2.exists()
    assert fo2.is_file()
    fo3 = outf / "Music/The Beatles/Magical Mystery Tour/The Beatles - Strawberry Fields Forever.mp3"
    assert fo3.exists()
    assert fo3.is_file()
    #
    # Tag consistency
    #
    audiofile = File(fo1, easy=True)  # easy=True for a unified dict-like interface
    assert audiofile is not None
    assert audiofile.get("artist", [""])[0] == "The Beatles"
    assert audiofile.get("title", [""])[0] == "Penny Lane"
    assert audiofile.get("album", [""])[0] == "Magical Mystery Tour"
    audiofile = File(fo2, easy=True)  # easy=True for a unified dict-like interface
    assert audiofile is not None
    assert audiofile.get("artist", [""])[0] == "The Beatles"
    assert audiofile.get("title", [""])[0] == "Hello, Goodbye"
    assert audiofile.get("album", [""])[0] == "Magical Mystery Tour"
    audiofile = File(fo3, easy=True)  # easy=True for a unified dict-like interface
    assert audiofile is not None
    assert audiofile.get("artist", [""])[0] == "The Beatles"
    assert audiofile.get("title", [""])[0] == "Strawberry Fields Forever"
    assert audiofile.get("album", [""])[0] == "Magical Mystery Tour"
    #
    # check the input folder
    # is it empty
    assert dir_empty(inf)  

def test_update_music_hierarchy(tmp_path):
    """ given a Music hierarchy in the input folder and an output folder identical
        to the input folder check that files are renamed and translocated a location
        based on their tags """
    #
    # Create music hierarchy in the infolder
    #
    inf = tmp_path / "in"
    inf.mkdir()
    musicf = inf / "Music"
    musicf.mkdir()
    #
    #
    #
    folder1 = musicf/ "Beatles"
    folder1.mkdir()
    albumf= folder1 / "MMT"
    albumf.mkdir()
    #
    # create several MP3 files in album folder title no tags
    #
    mk_mp3(albumf / "A - Penny.mp3", title="Penny Lane", artist="The Beatles", album="Magical Mystery Tour")
    mk_mp3(albumf / "B - Hello.mp3", title="Hello, Goodbye", artist="The Beatles", album="Magical Mystery Tour")
    mk_mp3(albumf / "C - Strawberry.mp3", title="Strawberry Fields Forever", artist="The Beatles", album="Magical Mystery Tour")
    #
    # Check input folder
    #
    fi1 = inf / "Music/Beatles/MMT/A - Penny.mp3"
    assert fi1.exists()
    assert fi1.is_file()
    fi2 = inf / "Music/Beatles/MMT/B - Hello.mp3"
    assert fi2.exists()
    assert fi2.is_file()
    fi3 = inf / "Music/Beatles/MMT/C - Strawberry.mp3"
    assert fi3.exists()
    assert fi3.is_file()
    #
    # Tag consistency
    #
    audiofile = File(fi1, easy=True)  # easy=True for a unified dict-like interface
    assert audiofile is not None
    assert audiofile.get("artist", [""])[0] == "The Beatles"
    assert audiofile.get("title", [""])[0] == "Penny Lane"
    assert audiofile.get("album", [""])[0] == "Magical Mystery Tour"
    audiofile = File(fi2, easy=True)  # easy=True for a unified dict-like interface
    assert audiofile is not None
    assert audiofile.get("artist", [""])[0] == "The Beatles"
    assert audiofile.get("title", [""])[0] == "Hello, Goodbye"
    assert audiofile.get("album", [""])[0] == "Magical Mystery Tour"
    audiofile = File(fi3, easy=True)  # easy=True for a unified dict-like interface
    assert audiofile is not None
    assert audiofile.get("artist", [""])[0] == "The Beatles"
    assert audiofile.get("title", [""])[0] == "Strawberry Fields Forever"
    assert audiofile.get("album", [""])[0] == "Magical Mystery Tour"
    #
    # attempt to restructure Music Hierarchy in place
    # 
    outf = inf
    fmf=FixMusicFile(infolder=inf, outfolder=outf, dry_run=False, overwrite=True)
    r = fmf.run()
    #
    #
    # check 3 files have been processed
    #
    assert r==3
    #
    # check the output - file existence
    #
    fo1 = outf / "Music/The Beatles/Magical Mystery Tour/The Beatles - Penny Lane.mp3"
    assert fo1.exists()
    assert fo1.is_file()
    fo2 = outf / "Music/The Beatles/Magical Mystery Tour/The Beatles - Hello, Goodbye.mp3"
    assert fo2.exists()
    assert fo2.is_file()
    fo3 = outf / "Music/The Beatles/Magical Mystery Tour/The Beatles - Strawberry Fields Forever.mp3"
    assert fo3.exists()
    assert fo3.is_file()
    #
    # Tag consistency
    #
    audiofile = File(fo1, easy=True)  # easy=True for a unified dict-like interface
    assert audiofile is not None
    assert audiofile.get("artist", [""])[0] == "The Beatles"
    assert audiofile.get("title", [""])[0] == "Penny Lane"
    assert audiofile.get("album", [""])[0] == "Magical Mystery Tour"
    audiofile = File(fo2, easy=True)  # easy=True for a unified dict-like interface
    assert audiofile is not None
    assert audiofile.get("artist", [""])[0] == "The Beatles"
    assert audiofile.get("title", [""])[0] == "Hello, Goodbye"
    assert audiofile.get("album", [""])[0] == "Magical Mystery Tour"
    audiofile = File(fo3, easy=True)  # easy=True for a unified dict-like interface
    assert audiofile is not None
    assert audiofile.get("artist", [""])[0] == "The Beatles"
    assert audiofile.get("title", [""])[0] == "Strawberry Fields Forever"
    assert audiofile.get("album", [""])[0] == "Magical Mystery Tour"
    #
    # check the input folder
    # 
    assert musicf.exists()
    assert not albumf.exists()
    assert not (musicf/ "Beatles").exists()

def test_update_flat_folder(tmp_path):
    """ given a folder with a flat list of music files as the input folder and an output folder identical
        to the input folder check that files are renamed and translocated a location
        based on their tags """
    #
    # Create music hierarchy in the infolder
    #
    inf = tmp_path / "in"
    inf.mkdir()
    #
    #
    #
    #
    # create several MP3 files in album folder title no tags
    #
    mk_mp3(inf / "A - Penny.mp3", title="Penny Lane", artist="The Beatles", album="Magical Mystery Tour")
    mk_mp3(inf / "B - Hello.mp3", title="Hello, Goodbye", artist="The Beatles", album="Magical Mystery Tour")
    mk_mp3(inf / "C - Strawberry.mp3", title="Strawberry Fields Forever", artist="The Beatles", album="Magical Mystery Tour")
    #
    # Check input folder
    #
    fi1 = inf / "A - Penny.mp3"
    assert fi1.exists()
    assert fi1.is_file()
    fi2 = inf / "B - Hello.mp3"
    assert fi2.exists()
    assert fi2.is_file()
    fi3 = inf / "C - Strawberry.mp3"
    assert fi3.exists()
    assert fi3.is_file()
    #
    # Tag consistency
    #
    audiofile = File(fi1, easy=True)  # easy=True for a unified dict-like interface
    assert audiofile is not None
    assert audiofile.get("artist", [""])[0] == "The Beatles"
    assert audiofile.get("title", [""])[0] == "Penny Lane"
    assert audiofile.get("album", [""])[0] == "Magical Mystery Tour"
    audiofile = File(fi2, easy=True)  # easy=True for a unified dict-like interface
    assert audiofile is not None
    assert audiofile.get("artist", [""])[0] == "The Beatles"
    assert audiofile.get("title", [""])[0] == "Hello, Goodbye"
    assert audiofile.get("album", [""])[0] == "Magical Mystery Tour"
    audiofile = File(fi3, easy=True)  # easy=True for a unified dict-like interface
    assert audiofile is not None
    assert audiofile.get("artist", [""])[0] == "The Beatles"
    assert audiofile.get("title", [""])[0] == "Strawberry Fields Forever"
    assert audiofile.get("album", [""])[0] == "Magical Mystery Tour"
    #
    # attempt to restructure Music Hierarchy in place
    # 
    outf = inf
    fmf=FixMusicFile(infolder=inf, outfolder=outf, dry_run=False, overwrite=True)
    r = fmf.run()
    #
    #
    # check 3 files have been processed
    #
    #assert r==3
    #
    # check the output - file existence
    #
    fo1 = outf / "Music/The Beatles/Magical Mystery Tour/The Beatles - Penny Lane.mp3"
    assert fo1.exists()
    assert fo1.is_file()
    fo2 = outf / "Music/The Beatles/Magical Mystery Tour/The Beatles - Hello, Goodbye.mp3"
    assert fo2.exists()
    assert fo2.is_file()
    fo3 = outf / "Music/The Beatles/Magical Mystery Tour/The Beatles - Strawberry Fields Forever.mp3"
    assert fo3.exists()
    assert fo3.is_file()
    #
    # Tag consistency
    #
    audiofile = File(fo1, easy=True)  # easy=True for a unified dict-like interface
    assert audiofile is not None
    assert audiofile.get("artist", [""])[0] == "The Beatles"
    assert audiofile.get("title", [""])[0] == "Penny Lane"
    assert audiofile.get("album", [""])[0] == "Magical Mystery Tour"
    audiofile = File(fo2, easy=True)  # easy=True for a unified dict-like interface
    assert audiofile is not None
    assert audiofile.get("artist", [""])[0] == "The Beatles"
    assert audiofile.get("title", [""])[0] == "Hello, Goodbye"
    assert audiofile.get("album", [""])[0] == "Magical Mystery Tour"
    audiofile = File(fo3, easy=True)  # easy=True for a unified dict-like interface
    assert audiofile is not None
    assert audiofile.get("artist", [""])[0] == "The Beatles"
    assert audiofile.get("title", [""])[0] == "Strawberry Fields Forever"
    assert audiofile.get("album", [""])[0] == "Magical Mystery Tour"
    #
    # check the input folder
    # 
    assert not fi1.exists()
    assert not fi2.exists()
    assert not fi3.exists()
