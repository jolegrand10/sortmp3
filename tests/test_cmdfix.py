""" test_cmdfix.py - Test for cmdfix.py """
import argparse
from sortmp3.cmdfix import CmdFix
import sys
import pytest


def test_invalid_priority(monkeypatch):
    test_args = ["prog", "--album", "Tag", "--artist", "Foo"]
    monkeypatch.setattr(sys, "argv", test_args)
    cf = CmdFix(argparse.ArgumentParser())
    with pytest.raises(SystemExit) as e:
        cf.parse()
    assert e.value.code != 0


def test_valid_priority(monkeypatch):
    test_args = ["prog", "--album", "Tag", "--artist", "File"]
    monkeypatch.setattr(sys, "argv", test_args)
    cf = CmdFix(argparse.ArgumentParser())
    cf.parse()
    assert cf.album == "Tag"
    assert cf.artist == "File"


def test_default(monkeypatch):
    """ Test the CmdFix command without any arg
     to check that defaults are those expected """
    test_args = ["cmdfix.py"]
    monkeypatch.setattr(sys, "argv", test_args)

    cf = CmdFix(argparse.ArgumentParser())
    cf.parse()
    assert cf.infolder == "."
    assert cf.outfolder == "."
    assert cf.artist == "Tag"
    assert cf.album == "Tag"
    assert cf.title == "Tag"
    assert cf.debug == False
    assert cf.verbose == False
    assert cf.dry_run == True
    assert cf.overwrite == False
