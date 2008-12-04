# -*- coding: utf-8 -*-
# Sébastien Renard (sebastien.renard@digitalfox.org)
# Code licensed under GNU GPL V2

# Simple shell for i10n administrative tasks

import cmd
import sys
import time
import locale

from django.db.models import Q
from django.core.exceptions import ValidationError

from py10n.dj10n.models import Branch, Module, Pofile, Translator

# Default user encoding. Used to decode all input strings
ENCODING=locale.getpreferredencoding()

# Force default encoding to prefered encoding
# This is mandatory when     output is piped in another command
reload(sys)
sys.setdefaultencoding(ENCODING)


class Shell(cmd.Cmd):
    def loop(self):
        self.prompt="py10n$ "
        banner="\nWelcome to py10n shell command line tool (sebastien@digitalfox.org)\n"
        banner+="Type 'help' for some help.\nUse Tab for completion\n"
        try:
            self.cmdloop(banner)
        except KeyboardInterrupt:
            self.__exit()
    
    def emptyline(self):
        # Do nothing instead of repeating last command
        pass
    
    # Command line definitions
    def do_exit(self, arg):
        self.__exit()    

    #Some alias
    do_quit=do_exit
    do_q=do_exit
    do_EOF=do_exit

    def onecmd(self, line):
        """This method is subclassed just to be
        able to decode user input"""
        #TODO:use a try/except bloc to catch all exceptions
        # Decode user input
        line=line.decode(ENCODING)
        return cmd.Cmd.onecmd(self, line)

    def do_doc(self, arg):
        self.do_po(arg, type='doc')

    def do_gui(self, arg):
        self.do_po(arg, type='gui')
    
    def do_po(self, arg, type='gui'):
        poList=Pofile.objects.filter(type=type).filter(name__icontains=arg)
        for po in poList:
            print "Name: %s / %s (%s)" % (po.module.name, po.name, po.module.branch.name)
            if po.translator:
                print "Translator: %s %s (since %s)" % (po.translator.firstname, po.translator.lastname, po.startdate)
            else:
                print "Available for booking"
            print "Untranslated : %s, fuzzy : %s" % (po.untranslated, po.fuzzy)
            print

    def do_guiDate(self, arg):
        self.do_poDate(arg, 'gui')

    def do_docDate(self, arg):
        self.do_poDate(arg, 'doc')

    def do_poDate(self, arg, type='gui'):
        if len(arg.split())!=2:
            print "Argument must be poName and bookingDate"
            return
        (name, date)=arg.split()
        try:
            po=Pofile.objects.get(name=name, type=type) 
            po.startdate=date
            po.save()
            print "PO updated"
        except ValidationError, e:
            print e
        except Pofile.DoesNotExist:
            pos=Pofile.objects.filter(name__icontains=name).filter(type=type)
            if pos.count()>0:
                print "More than one PO match : %s" % ", ".join([po.name for po in pos])
            else:
                print "No PO match your request"

    def do_docTranslator(self, arg):
        self.do_translator(arg, type='doc')
    
    def do_guiTranslator(self, arg):
        self.do_translator(arg, type='gui')

    def do_translator(self, arg, type='gui'):
        for translator in Translator.objects.filter(Q(firstname__icontains=arg) |
                                                    Q(lastname__icontains=arg)  |
                                                    Q(email__icontains=arg)):
            pos=", ".join([po.name for po in translator.pofile_set.filter(type=type)])
            print "%s (%s): %s" % (unicode(translator), translator.email, pos)
    
    def do_addTranslator(self, arg):
        # Remove quotes and < > from name
        for i in ("'", '"', "<", ">"):
            arg=arg.replace(i, " ")
        
        if len(arg.split())!=3:
            print "Argument must be like : jean dupont jdupont5444@yahoo.fr"
            return
        
        (firstname, lastname, mail)=arg.split()
        mail=mail.replace("@", "_AT_") # To avoid too easy spam
        translator=Translator()
        translator.firstname=firstname
        translator.lastname=lastname
        translator.email=mail
        translator.save()
    
    def do_docReservation(self, arg):
        self.do_reservation(arg, type='doc')

    def do_guiReservation(self, arg):
        self.do_reservation(arg, type='gui')

    def do_reservation(self, arg, type='gui'):
        translatorName=None
        poListName=None
        translator=None
        try:
            # Remove commas if any and split arguments
            arg=arg.replace(","," ").split()
            translatorName=arg.pop(0)
            poListName=arg
            if len(poListName)==0:
                print "Give at least one PO to reserve !"
                return
        except Exception, e:
            print "This function takes at least two arguments !"
            print "\nUsage : "
            self.help_reservation()
            return
        # Translator selection
        translator=self.__selectTranslator(translatorName)
        #TODO: create a py10nShellException to handle errors correctly
        if translator=="error":
            return
        
        # Removing extension .po or .pot to filename if any
        for ext in (".po", ".pot"):
            poListName=[self.__reduceExt(poName, ext) for poName in poListName]

        # PO selection
        for poName in poListName:
            try:
                pos=[Pofile.objects.get(name=poName, type=type),]
            except Pofile.DoesNotExist:
                pos=self.__selectPo(poName, type)
            if not pos:
                print "Sorry, no PO selected, skiping to next (if any)"
                continue
            
            for po in pos:
                if po.translator is None:
                    self.__reservePo(translator, po)
                else:
                    print "%s is already reserved by %s" % (po, unicode(po.translator))
                    print "Really change %s reservation ? (yes/no)" % po
                    answer=sys.stdin.readline()
                    answer=answer.strip()
                    if answer=="yes" or answer=="y":
                        self.__reservePo(translator, po)
                    else:
                        print "Reservation is canceled for %s" % po

    def do_guiSwitch(self, line):
        """Switch a gui module from a branch to another
        guiSwitch <branch name> <module 1> <module 2>..."""
        self.do_switch(line, type="gui")

    def do_docSwitch(self, line):
        """Switch a doc module from a branch to another
        docSwitch <branch name> <module 1> <module 2>..."""
        self.do_switch(line, type="doc")

    def do_switch(self, line, type="gui"):
        """Switch a module from a branch to another"""
        arg=line.split()
        if len(arg)<2:
            print "Needs at least two arguments : branch name and module name"
            return
        branchName=arg.pop(0)
        try:
            branch=Branch.objects.get(name=branchName)
        except Branch.DoesNotExist:
            print "Branch %s does not exist" % branchName
            return
        
        for moduleName in arg:
            try:
                print "Moving module %s to branch %s..." % (moduleName, branch)
                module=Module.objects.get(name=moduleName)
                module.branch=branch
                module.save()
            except Module.DoesNotExist:
                print "=>Module %s does not exist (skipping)" % moduleName
                continue
            except Module.MultipleObjectsReturned:
                print "=>Module %s exists in multiple branch (skipping)" % moduleName

    def do_docModule(self, arg):
        self.do_module(arg, type='doc')

    def do_guiModule(self, arg):
        self.do_module(arg, type='gui')

    def do_module(self, arg, type='gui'):
        moduleList=Module.objects.filter(type=type).filter(name__icontains=arg)
        for module in moduleList:
            print "%s (%s)" % (module.name, module.branch.name)

    # Command help definitions
    def help_gui(self):
        print "Search for gui PO file"
        print "gui <gui po name or partial name>"
    
    def help_doc(self):
        print "Search for doc PO file"
        print "doc <doc po name or partial name>"

    def help_guiTranslator(self):
        print "Search for GUI translator and display its reservation"
        print "guiTranslator <translator firstname or lastname or partial firstname or lastname>"
    
    def help_docTranslator(self):
        print "Search for doc translator and display its reservation"
        print "docTranslator <translator firstname or lastname or partial firstname or lastname>"

    def help_guiReservation(self):
        print "guiReservation <translator firstname or lastname> <PO1> <PO2> ... "
        print "univocal partial name can be used for both translator and POs"

    def help_docReservation(self):
        print "docReservation <translator firstname or lastname> <PO1> <PO2> ... "
        print "univocal partial name can be used for both translator and POs"

    def help_guiDate(self):
        print "Change po booking date"
        print "guiDate <po name> <date>"
    
    def help_docDate(self):
        print "Change po booking date"
        print "docDate <po name> <date>"
        
    # Help alias
    help_po=help_gui
    help_translator=help_guiTranslator
    help_reservation=help_guiReservation
    help_poDate=help_guiDate
    
    # Helper functions
    def __selectTranslator(self, translatorName):
        """ Select a translator from a name"""
        if translatorName.lower()=="nobody" or translatorName.lower()=="unknown":
            print "Found the unknown translator"
            return None
        
        # Get real translator
        #TODO: use /get() and DoesNotExist and MultipleObjectsReturn exceptions instead of count() to make code cleaner 
        translators=Translator.objects.filter(Q(firstname__icontains=translatorName) |
                                              Q(lastname__icontains=translatorName))
        if translators.count()==0:
            print "No translator match %s." % translatorName
            return "error"
        elif translators.count()==1:
            print "Found translator %s." % unicode(translators[0])
            return translators[0]
        else:
            print "Multiple translator match %s. Please select the good one : \n" % translatorName
            i=1
            for translator in translators:
                print "(%d) %s" % (i, unicode(translator))
                i+=1
            answser=sys.stdin.readline()
            try:
                return translators[int(answser)-1]
            except Exception:
                print "Invalid number"
                return "error"
    
    def __selectPo(self, poName, type):
        """ Select a PO from a name"""
        pos=Pofile.objects.filter(name__icontains=poName).filter(type=type)
        if pos.count()==0:
            print "No PO match %s." % poName
            return None
        elif pos.count()==1:
            print "Found PO %s" % pos[0]
            return pos[0]
        else:
            print "Multiple PO match %s. Please select the good one: \n" % poName
            print "(0) All"
            i=1
            for po in pos:
                print "(%d) %s / %s (%s)" % (i, po.module, po, po.module.branch)
                i+=1
            answer=sys.stdin.readline()
            try:
                answer=int(answer)
                if answer==0:
                    return pos
                else:
                    return [pos[int(answer)-1]]
            except Exception, e:
                print "Invalid number %s" % e
                return None
            
    def __reservePo(self, translator, po):
        po.translator=translator
        if translator is None:
            po.startdate=None
        else:
            po.startdate=time.strftime('%Y-%m-%d')
        po.save()
        print "Reservation updated for %s" % po.name
    
    def __reduceExt(self, name, ext):
        """Remove extension ext from name"""
        if name.endswith(ext):
            name=name[0:len(name)-len(ext)]
        return name

    def __exit(self):
        print "\n\nBye !\n"
        sys.exit(0)