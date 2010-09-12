# -*- coding: UTF-8 -*-

# Sébastien Renard (sebastien.renard@digitalfox.org)
# Code licensed under GNU GPL V2

"""Tools to ease coordinator workflow"""

from py10n.dj10n.models import Pofile
from py10n.dj10n.pology import posieve
from py10n.settings import PY10N_LANG

from os import listdir
from os.path import join
from shutil import move

def movePos(path, type="gui", check=True):
    """Move po file to their good place in SVN prior to commit
    @param pos: list of po file names
    @param type: gui or doc
    @type type: str
    @param check: also check files with Pology (default is True)"""
    pos = [f for f in listdir(path) if f.endswith(".po")]
    if len(pos) == 0:
        print "No po file found"
        return
    print "About to move %s pos" % len(pos)
    for poName in pos:
        try:
            print "======== %s ========" % poName
            po = Pofile.objects.get(name=poName[:-3], type=type)
            destPath = po.poFilePath()
            #BUG: if destPath dir does not exit it should be created
            move(join(path, poName), destPath)
            print "Move %s to %s (booked by %s)" % (poName, destPath, po.translator)
            if check:
                for sieve, options in (("check_rules", (("lang", PY10N_LANG),)),
                                       ("check_spell", (("lang", PY10N_LANG),)),
                                       ("-c check_kde4", ())):
                    print "Checking %s with %s" % (poName, sieve)
                    posieve(sieve, options, destPath)
        except Pofile.DoesNotExist:
            print "%s not found. Skipping" % poName
            continue
        except Pofile.MultipleObjectsReturned:
            print "More than one PO match %s. Do it manually" % poName
            continue
