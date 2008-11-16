# -*- coding: UTF-8 -*-

# Sébastien Renard (sebastien.renard@digitalfox.org)
# Code licensed under GNU GPL V2

from py10n import settings

import md5, os
from os.path import join

def computePoHashValue(path):
    """Compute and return  file hash value"""
    try:
        content=file(path)
        hashValue=md5.new(content.read()).hexdigest()
        content.close()
        return hashValue
    except Exception, e:
        print "Ouh, something bad happens while opening file %s for md5 computation. Error was : %s" % (path, e)

def updateGettextStats(po):
    result=""
    try:
        process=os.popen("LANG=C; msgfmt --statistics "+po.filePath()+" 2>&1")
        result=process.readlines()
        process.close()
    except Exception, e:
        print "Cannot get statistics for file %s. Error was : %s" % (po.filePath(), e)

    # Set to zero all gettext stats
    po.translated=0
    po.fuzzy=0
    po.untranslated=0

    # Set new value
    for stat in result[0].split(","):
        stats=stat.split()
        if(stats[1]=="translated"):
            po.translated=int(stats[0])
        elif(stats[1]=="fuzzy"):
            po.fuzzy=int(stats[0])
        elif(stats[1]=="untranslated"):
            po.untranslated=int(stats[0])
        else:
            print "Ouh. Something bad happens with msgfmt for po %s. Output was : %s" % (po.name, stat)

def updatePologyStats(po, pologyXmlStat):
    if pologyXmlStat is not None and not po.isPot():
        if pologyXmlStat.has_key(po.name):
            po.error=pologyXmlStat[po.name]
        else:
            print "Pology stat not found for %s." % po.name

def messagePath(type, template):
    """Build the message path
    @param type: gui or doc
    @param template: True or False
    @returns: path as a str"""
    if template:
        if type=="gui":
            return "templates/messages"
        else:
            return "templates/docmessages"
    else:
        if type=="gui":
            return join(settings.PY10N_LANG, "messages")
        else:
            return join(settings.PY10N_LANG, "docmessages")
