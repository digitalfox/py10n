# -*- coding: UTF-8 -*-

# Sébastien Renard (sebastien.renard@digitalfox.org)
# Code licensed under GNU GPL V2

from py10n import settings

import os
from os.path import abspath, dirname, exists, isdir, join
try:
    from hashlib import md5
except ImportError:
    # before python 2.5 hashlib did not exist
    from md5 import md5

def computePoHashValue(path):
    """Compute and return  file hash value"""
    try:
        content = file(path)
        hashValue = md5(content.read()).hexdigest()
        content.close()
        return hashValue
    except Exception, e:
        print "Ouh, something bad happens while opening file %s for md5 computation. Error was : %s" % (path, e)

def updateGettextStats(po):
    result = ""
    try:
        path = po.poFilePath()
        if not exists(path):
            # Use template
            path = po.filePath()
        process = os.popen("LANG=C; msgfmt --statistics %s 2>&1" % path)
        result = process.readlines()
        process.close()
    except Exception, e:
        print "Cannot get statistics for file %s. Error was : %s" % (po.filePath(), e)

    # Set to zero all gettext stats
    po.translated = 0
    po.fuzzy = 0
    po.untranslated = 0

    # Set new value
    for stat in result[0].split(","):
        stats = stat.split()
        if(stats[1] == "translated"):
            po.translated = int(stats[0])
        elif(stats[1] == "fuzzy"):
            po.fuzzy = int(stats[0])
        elif(stats[1] == "untranslated"):
            po.untranslated = int(stats[0])
        else:
            print "Ouh. Something bad happens with msgfmt for po %s. Output was : %s" % (po.name, stat)

def updatePologyStats(po, pologyXmlStat):
    if pologyXmlStat is not None and not po.isPot():
        if pologyXmlStat.has_key(po.name):
            po.error = pologyXmlStat[po.name]
        else:
            print "Pology stat not found for %s." % po.name

def messagePath(type, template, branch):
    """Build the message path
    @param type: gui or doc
    @param template: True or False
    @param branch: branch name, used to detect special branch path like summit branch
    @returns: path as a str"""
    if branch == "summit":
        prefix = "summit"
    else:
        prefix = ""
    if template:
        if type == "gui":
            return join("templates", prefix, "messages")
        else:
            return join("templates", prefix, "docmessages")
    else:
        if type == "gui":
            return join(settings.PY10N_LANG, prefix, "messages")
        else:
            return join(settings.PY10N_LANG, prefix, "docmessages")

def checkFile(filename):
    """Check it is possible to write filename
    @return: True if ok, else False"""
    filename = abspath(filename)
    if isdir(filename):
        print "%s is a directory. Please give a full path with a filename as argument." % filename
        return False
    if exists(filename):
        if not os.access(filename, os.W_OK):
            print "File %s is not writable !" % filename
            return False
    else:
        if not os.access(dirname(filename), os.W_OK):
            print "Directory %s is not writable !" % dirname(filename)
            return False
    return True
