# SortMP3 #

This is a Python script based on Mutagen to sort and store MP3 and M4A music files : it moves files, updates consistently names and tags to fit them in a Music Hierarchy based on Artist-Album-Title. 

# Usage
```
usage: cmdfix.py [-h] [-i INFOLDER] [-o OUTFOLDER] [--artist ARTIST] [--album ALBUM] [--title TITLE] [-v] [-d] [--dry_run]

Fix Music File looks for music files in the infolder and transfers them to the outfolder. Each file is located in the Music
Hierarchy, i.e. Music / Artist / Album / Title,  according to its TAGs. Missing tags are adjusted with information found in filenames.     
Priority is given either to Tag or File information to settle conflicts for items such as artist, title or album.

options:
  -h, --help            show this help message and exit
  -i INFOLDER, --infolder INFOLDER
                        Input folder. Default is current folder.
  -o OUTFOLDER, --outfolder OUTFOLDER
                        Output folder. Default is current folder.
  --artist ARTIST       Specify File or Tag
  --album ALBUM         Specify File or Tag
  --title TITLE         Specify File or Tag
  -v, --verbose         Show info messages in log
  -d, --debug           Show debugging details
  --dry_run             Show file moves but leave music files unchanged
```

# Features

## Infer Artist and Title fields from the filename

Provided that the syntax of the filename is stricty
`Artist - Title.mp3` or `m4a`

## Infer the Album name for the folder name
If the music file lies in a folder with a meaningful name, this name is taken as a candidate for the Album name

"Meaningful" means a name created specifically to host a bunch of music files under the input folder. The name of the global input folder itself is not considered meaningful.


## Music Hierarchy

The Music Hierarchy is  a folder hierarchy starting with the Music folder.
The next level is one folder per Artist.
If -for some reason- this piece of info is lacking, "Unknown artist" is used as a default value.
The level after, is one folder per Album.
When Album info is missing "Single" is used as a default value.
The next level is that of music files:  Artist - Title.mp3 is the preferred and expected syntax.


## File info versus MP3 or M4A tags
Information inferred from the file path and information originating from the TAGS included in the Music File Header are merged according to user defined priorities.

A priority can by either "File" or "Tag".

Priorities are applied to the Artist, Album, Title attributes.

Default priority is to "Tag".

This means that if a non empty Tag is available, it is preferred to an element extracted from the filepath and a default value will be used in case both have failed.

If File is chosen as a priority, the same thing happens but File info is used first if available and Tag is tried next. In case both are vacant, a default value is used.

Priorities may be defined independently for Artist, Album and Title.

## Fixing a tune

"Fixing a tune" means moving a music file from the input folder to a Music hierarchy in the output folder.

The tune is moved to an Artist/Album/Title location, under the Music folder in the output folder.

In addition, the TAGs in the header are set consistently with the retained info for Artist/Album/Title.

## Default information

In case info is missing in both file/tags, default values are introduced:
`Single`for a missing album name, `Unknown artist`for a missing artist name.
`Unknown title`is the default for a missing title.

## Name standardization

Names (Artists, Album, Titles) are stripped from leading and trailing spaces. In addition they are converted to a mix of uppercase and lowercase so that each word starts with an uppercase letter.


## Name sanitization

Characters that do not fit in filenames like "*" or ":" are substituted by spaces.

## Dry run

`dry_run=True` is the default. This means that when the fix command runs without further details the proposed file moves will be shown but not executed.

To actually move the files and modify their tags in their headers, `dry_run=False` must be used.


Priority is given to the existing MP3 tags for Artist/Album/Title.
Should any of those pieces of information be missing, it will be replaced by info found in the file path.
Artist will be supplied by the folder name.
Title will be extracted from the file name.

## Information logging

A log file is produced. Messages are directed both to standard output and to a file. The log file is limited in size (100k) and 3 versions are used with rotating log file policy.

# Software

## Style

`pathlib` is preferred to `os`.

## cmdfix.py
Provides the CLI interface. Collects the args from the command line and passes them to the fix.py script.
Args such as verbose and debug drive the behavior of the logging facility.

## fix.py
This is the home of the FixMusicFile class.

# Tests

Pytest is used. 


# TODOs

- Use absolute paths for in- out- folders : os.path.abspath('.'))
- Provide a defaut for absent title
- Process track numbers or Album names in the filename 
- Test name sanitization


