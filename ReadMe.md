# SortMP3 #

This is a set of Python scripts using EyeD3.

## Infer Artist and Title fields

When the filenames matches the pattern Artist - Title
and their type is .mp3,
provided that there are no conflicts with existing tags, ie, the corresponding tags are empty
add the Artist and Title Tags with the values found in the filename

EyeD3 and Mutagen librairies are both used. 
EyeD3 fails when the Genre Tag has a forbidden value. 
Mutagen is then used to fix this value to a default value. 
"Other" is used as the default value for the Genre Tag.

This is done by fn2at, a script that expects 2 parameters, the input and the output folders.

Files remaining in the input folder are not viable or do need to be fixed manually.
(Usually their name needs to be corrected to obey strictly the syntax
Artist - Title.mp3)

## Music Hierarchy

The Music Hierarchy is  a folder hierarchy starting with the Music folder.
The next level is one folder per Artist.
If -for some reason- this piece of info is lacking, "Unknown artist" is used as a default value.
The level after, is one folder per Album.
When Album info is missing "Single" is used as a default value.
The next level is that of music files:  Artist - Title.mp3 is the preferred syntax.
Track numbers or Album name in the filename are not processed so far (Maybe TODO)

## Move single tunes
The mvsingle.py script moves an isolated music file, knowing its title and the artist, but possibly missing the info about the album to the right place in the  Music hierarchy.
Album information is inferred from Tag Album in ht MP3 header. If missing, then "Single" is used as a default album name.
m4a files are not processed for the time being (TODO)

## Move full album
The mvalbum.py script moves a full album its right place in the music hierarchy.

An album in general is made of a folder with an explicit artist and album title in the name of the folder and optional rank + tune titles in its content.

## FixMusicFile

This scripts takes two arguments. The first one is a folder where unsorted music files are found, the second one is the folder where the Music/Artist/Album hierarchy lives.

All the files in the input folder are analysed. 

If a music file is recognized, then its place is determined in the Music Hierarchy.
Priority is given to the existing MP3 tags for Artist/Album/Title.
Should any of those pieces of information be missing, it will be replaced by info found in the file path.
Artist will be supplied by the folder name.
Title will be extracted from the file name.

## FixMusicFolder

TODO NEXT



