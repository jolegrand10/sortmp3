""" Script cmdfix.py - CLI interface for FixMusicFile """
import argparse
from sortmp3.fullog import Full_Log
import logging
from sortmp3.fix import FixMusicFile

DEBUG = True

class CmdFix:
    """ a command to run FixMusicFile from the  """
    def __init__(self, p):
        """ p is the parser, provided at init time to facilitate unit testing"""
        self.parser = p
        self.setup_parser()
        self.infolder = "."
        self.outfolder = "."
        self.artist = "Tag"
        self.album = "Tag"
        self.title = "Tag"
        self.debug = DEBUG
        self.verbose = False

    def is_valid_priority(self, arg):
        if type(arg) is not str:
            self.parser.error(f"Priority should be a string")
        else:
            arg = arg.capitalize()
            if arg not in {'File', 'Tag'}:
                self.parser.error(f"Priority should be File or Tag")
            else:
                return arg

    def setup_parser(self):
        """ add args to parser p"""
        self.parser.add_argument('-i', '--infolder', dest='infolder',
                                 help='Input folder.  Default is current folder.',
                                 default=".")
        self.parser.add_argument('-o', '--outfolder', dest='outfolder',
                                 help='Output folder. Default is current folder.',
                                 default=".")

        self.parser.add_argument('--artist', help='Specify File or Tag',
                                 type=lambda x: self.is_valid_priority(x),
                                 default="Tag")
        self.parser.add_argument('--album', help='Specify File or Tag',
                                 type=lambda x: self.is_valid_priority(x),
                                 default="Tag")
        self.parser.add_argument('--title', help='Specify File or Tag',
                                 type=lambda x: self.is_valid_priority(x),
                                 default="Tag")
        self.parser.add_argument('-v', '--verbose', help='Show info messages in log',
                                 action='store_true', default=False)
        self.parser.add_argument('-d', '--debug', help='Show debugging details',
                                 action='store_true', default=False)
        self.parser.add_argument('--dry_run', help='Show file moves but leave music files unchanged',
                                 action='store_true', default=True)

        self.parser.description = """ Fix Music File looks for music files in the infolder and transfers them
         to the outfolder. Each file is located in the Music Hierarchy. Music / Artist / Album / Title according
        to its TAGs. Missing tags are adjusted with information found in filenames. Priority is given to Tag or File
        to settle conflicting info for artist, title, album. """

    def parse(self, args=None):
        pa = self.parser.parse_args(args)
        self.infolder = pa.infolder
        self.outfolder = pa.outfolder
        self.artist = pa.artist
        self.title = pa.title
        self.album = pa.album
        self.debug = pa.debug
        self.verbose = pa.verbose
        self.dry_run = pa.dry_run
        if DEBUG:
            #
            # check parsed args
            #
            for k in dir(pa):
                if not k.startswith('_'):
                    logging.debug(f"  {k}: {eval('pa.' + k)}")

    def run(self):
        try:
            fixer = FixMusicFile(self.infolder, self.outfolder, artist=self.artist,
                                 title=self.title, album=self.album)
            # fixer.run()
        except Exception as e:
            logging.error(f"Fixer failed. Reason: {e}")


def main():
    c = CmdFix(argparse.ArgumentParser())
    Full_Log("FixMusicFile", debug=DEBUG, verbose=c.verbose)
    c.parse()
    c.run()


if __name__ == '__main__':
    main()
