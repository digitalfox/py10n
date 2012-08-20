#!/usr/bin/python
# -*- coding: utf-8 -*-

# Sébastien Renard (sebastien.renard@digitalfox.org)
# Code licensed under GNU GPL V2

"""Py10n main command line tool"""

## Setup django envt & django imports
from django.core.management import setup_environ, execute_manager
import settings
setup_environ(settings)


from py10n.dj10n.views  import translatorsPage, bookingPage, statsPage
from py10n.dj10n.models import Pofile, Branch, Module
from py10n.dj10n.utils  import computePoHashValue, checkFile, updateGettextStats, updatePologyStats
from py10n.dj10n.commit import movePos
from py10n.dj10n.shell import Shell
from py10n.dj10n.pology import posieve


from os.path import abspath, exists, isdir, join
from os import listdir
from optparse import OptionParser
from sys import exit
import codecs
import re

SIEVES = {"check_rules":"pology-rules-errors.xml",
       "check-spell":"pology-spell-errors.xml"}


def poStat(pologyXmlStat, type='gui'):
    """Update PO statistics"""
    for po in Pofile.objects.filter(type=type):
        path = po.poFilePath()
        if not exists(path):
            path = po.filePath()

        md5sum = computePoHashValue(path)
        if po.md5sum != md5sum:
            print "Processing %s" % po.name
            updateGettextStats(po)
            updatePologyStats(po, pologyXmlStat)
            po.md5sum = md5sum
            po.save()

def readPologyXmlStat(pologyXmlPath):
    """Read number of errors for each po in pology xml error summary
    @return: hash array with po name as key and number of error as value"""
    pologyXmlStat = {}
    poString = re.compile(u'<po name="(.+).po">')
    print "Load errors from pology xml file..."
    for xmlFile in SIEVES.values():
        for line in codecs.open(join(pologyXmlPath, xmlFile), "r", "utf-8"):
            result = poString.match(line)
            if result:
                count = 0
                name = result.group(1)
            elif u"<error>" in line:
                count += 1
            elif u"</po>" in line:
                if pologyXmlStat.has_key(name):
                    pologyXmlStat[name] += count
                else:
                    pologyXmlStat[name] = count
    return pologyXmlStat

def createPologyXMLStat(pologyXmlPath, type="gui", sieve="check_rules"):
    """Create POlogy xml errors file for all modules
    @param pologyXMLPath: Path where XML file will be write"""
    #TODO: use new function from Pology modules
    mPath = " ".join([join(settings.PY10N_FILE_BASEPATH, m.poPath()) for m in Module.objects.filter(type=type) if m.pofile_set.count() > 0])
    posieve(sieve, [("xml", join(pologyXmlPath, SIEVES[sieve])), ("lang", settings.PY10N_LANG)], mPath)

def sync(type="gui"):
    """Sync filesystem modules and po files with database"""

    if type == "gui":
        modulePath = "templates/messages"
    else:
        modulePath = "templates/docmessages"

    dbTrunkModuleList = [m.name for m in Module.objects.filter(type=type)]

    for branch in Branch.objects.all():
        path = join(settings.PY10N_FILE_BASEPATH, branch.path, modulePath)
        try:
            fsModuleList = listdir(path)
        except OSError, e:
            print "Cannot find template dir for branch %s (%s)" % (branch.name, e)
            continue

        if branch.name == "trunk":
            # Adding modules in trunk only
            for moduleName in fsModuleList:
                if moduleName == ".svn" or moduleName in dbTrunkModuleList:
                    continue
                else:
                    print "Adding %s (%s) module to database" % (moduleName, branch.name)
                    m = Module()
                    m.branch = branch
                    m.name = moduleName
                    m.type = type
                    m.save()

        # Removing modules
        for module in branch.module_set.filter(type=type):
            if module.name not in fsModuleList:
                if module.pofile_set.count() == 0:
                    print "Removing module %s (%s)" % (module.name, module.branch.name)
                    module.delete()
                else:
                    print "Module %s (%s) does not exist anymore but still have pofile." % (module.name, branch.name)

    # Adding/removing po
    poToBeRemoved = set() # Don't destroyed immediately PO to detect their move

    # Removing po
    for module in Module.objects.filter(type=type):
        path = join(settings.PY10N_FILE_BASEPATH, module.branch.path, modulePath, module.name)
        dbPoList = [f.name for f in module.pofile_set.all()]
        try:
            fsPoList = [p[:-4] for p in listdir(path) if p != ".svn"]
            #print list(fsPoList)
        except OSError, e:
            print "Cannot find module %s at %s (%s). Skipping" % (module.name, path, e)
            continue

        for po in module.pofile_set.all():
            if po.name not in fsPoList:
                print "File %s is gone from module %s" % (po.name, module.name)
                poToBeRemoved.add(po)

    # Adding po (in a separate loop to track on po move)
    for module in Module.objects.filter(type=type):
        path = join(settings.PY10N_FILE_BASEPATH, module.branch.path, modulePath, module.name)
        dbPoList = [f.name for f in module.pofile_set.all()]
        try:
            fsPoList = [p[:-4] for p in listdir(path) if p[-4:] == ".pot"]
            #print list(fsPoList)
        except OSError, e:
            print "Cannot find module %s at %s (%s). Skipping" % (module.name, path, e)
            continue

        for poName in fsPoList:
            if poName in dbPoList:
                continue
            else:
                # Looking for po to be removed that can be undeleted
                for po in poToBeRemoved:
                    if po.name == poName and po.type == type:
                        print "Moving %s from %s to %s" % (po.name, po.module.name, module.name)
                        po.module = module
                        po.save()
                        poToBeRemoved.remove(po)
                        break
                else:
                    print "Adding %s in %s module" % (poName, module.name)
                    p = Pofile()
                    p.module = module
                    p.name = poName
                    p.type = type
                    p.save()
    # Really remove po that no longer exist
    for po in poToBeRemoved:
        print "Removed from database : %s/%s (%s)" % (po.module.name, po.name, po.module.branch.name)
        po.delete()

def parseOptions():
    """Command line option parsing"""
    parser = OptionParser()

    # Pages generation
    parser.add_option("-f", "--file", dest="filename",
              help="Write page to FILE")
    parser.add_option("-x", "--xml", dest="pologyXml",
              help="Path to pology XML error directory where live pology-rules-errors.xml and pology-spell-errors.xml")
    parser.add_option("-t", "--type", dest="type",
              type="choice", choices=["po", "translator", "stat"],
              help="Page type (can be po, translator or stat)")
    # Sync
    parser.add_option("-s", "--sync", dest="sync", action="store_true",
              help="Synchronise database with files")
    # Update SVN
    parser.add_option("-u", "--udpate", dest="update", action="store_true",
              help="Update from svn")
    # Gettext and Pology statistics
    parser.add_option("-p", "--po-stat", dest="poStat", action="store_true",
              help="Compute gettext and Pology messages statistics (collect from xml file)")
    # Create/Update pology xml error statistics
    parser.add_option("-e", "--errors", dest="errorsStat", action="store_true",
              help="Create/Update Pology messages statistics into XML file (see -x)")
    # Shell
    parser.add_option("-c", "--commandLine", dest="shell", action="store_true",
              help="Command line tool (shell) for py10n")
    # Doc or gui ?
    parser.add_option("-d", "--doc", dest="doc", action="store_true",
              help="Work with documentation (exclusive with --gui switch)")
    parser.add_option("-g", "--gui", dest="gui", action="store_true",
              help="Work with application/gui (exclusive with --doc switch)")
    parser.add_option("-w", "--web", dest="web", action="store_true",
              help="Start the administration web interface")
    parser.add_option("-m", "--move", dest="move",
              help="Move po files to the right place to be committed")
    return parser.parse_args()

def main():
    """Main entry point"""
    (options, args) = parseOptions()

    # What do we want to do ?
    if options.shell:
        Shell().loop()

    if options.web:
        execute_manager(settings, argv=[__file__, "runserver"])
        exit(0)

    if options.doc and options.gui:
        print "You must choose doc *or* gui, but not both ! (see --help)"
        exit(1)

    if options.doc:
        type = "doc"
    elif options.gui:
        type = "gui"
    else:
        print "You must choose either doc (-d) or gui (-g)"
        exit(1)

    if options.filename and not options.type:
        print "Type must be defined for page generation (see --help)"
        exit(1)
    elif not options.filename and options.type:
        print "Filename must be defined for page generation (see --help)"
        exit(1)
    elif options.filename and options.type:
        # Check file
        if not checkFile(options.filename):
            exit(1)
        # Choose correct type
        if options.type == "po":
            print "Creating PO page"
            file(options.filename, "w").write(bookingPage(type).encode("UTF-8"))
        elif options.type == "translator":
            print "Creating Translator page"
            file(options.filename, "w").write(translatorsPage(type).encode("UTF-8"))
            file(options.filename[:-3] + "csv", "w").write(translatorsPage(type, format="csv").encode("UTF-8"))
        elif options.type == "stat":
            print "Creating statistics page"
            file(options.filename, "w").write(statsPage(type).encode("UTF-8"))
        else:
            print "Ouha. Something goes wrong, type should have be correctly defined here !!!"
            exit(1)
    elif options.update:
        print "Update from SVN is not yet implemented"
    elif options.sync:
        sync(type=type)
    elif options.poStat:
        if options.pologyXml:
            poStat(readPologyXmlStat(options.pologyXml), type=type)
        else:
            print "pology XML path must be defined for this action"
            exit(1)
    elif options.errorsStat:
        if options.pologyXml:
            for sieve in SIEVES.keys():
                createPologyXMLStat(options.pologyXml, sieve=sieve, type=type)
        else:
            print "pology XML path must be defined for this action"
            exit(1)
    elif options.move:
        path = abspath(options.move)
        if not isdir(path):
            print "%s is not a directory" % options.move
            exit(1)
        movePos(path, type=type)
    else:
        print "Use --help for help"
        exit(1)

if __name__ == "__main__":
    main()
