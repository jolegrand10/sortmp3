# SortMP3 #

This is a set of Python scripts using EyeD3.

## Infer Artist and Title fields

When the filenames matches the pattern Artist - Title,
provided that there are no conflicts with existing tags, ie, the corresponding tags are empty
add the Artist and Title Tags with the values found in the filename

EyeD3 and Mutagen librairies are both used. EyeD3 fails when the Genre Tag has a forbidden value. Mutagen is then used to fix this value to a default value. "Other" is used as the default value for the Genre Tag.

This is done by fn2at, a script that expects 2 parameters, the input and the output folders.

## Dispatch files in repo

The repo structure is
Music - Artist - Album | Single - Title

## Move single tunes
The mvsingle.py script moves an isolated music file, knowing its title and the artist, but possibly missing the info about the album to the right place in the  Music hierarchy.

## Move full album
The mvalbum.py script moves a full album its right place in the music hierarchy.

An album in general is made of a folder with an explicit artist and album title in the name of the folder and rank + tune titles in its content.




