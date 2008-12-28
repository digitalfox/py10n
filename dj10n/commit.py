# -*- coding: UTF-8 -*-

# Sébastien Renard (sebastien.renard@digitalfox.org)
# Code licensed under GNU GPL V2

"""Tools to ease coordinator workflow"""

from py10n.dj10n.models import Pofile

from os import listdir
from os.path import join
from shutil import move

def movePos(path, type="gui"):
    """Move po file to their good place in SVN prior to commit
    @param pos: list of po file names"""
    pos=[f for f in listdir(path) if f.endswith(".po")]
    if len(pos)==0:
        print "No po file found"
        return
    print "About to move %s pos" % len(pos)
    for poName in pos:
        try:
            po=Pofile.objects.get(name=poName[:-3], type=type)
            destPath=po.poFilePath()
            move(join(path, poName), destPath)
            print "Move %s to %s (booked by %s)" % (poName, destPath, po.translator)
        except Pofile.DoesNotExist:
            print "%s not found. Skipping" % poName
            continue
        except Pofile.MultipleObjectsReturned:
            print "More than one PO match %s. Do it manually" % poName
            continue
 