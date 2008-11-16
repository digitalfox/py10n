# -*- coding: UTF-8 -*-

# Sébastien Renard (sebastien.renard@digitalfox.org)
# Code licensed under GNU GPL V2

from django.db import models
from django.contrib import admin

from py10n import settings
from py10n.dj10n.utils import messagePath

from os.path import join

TYPES=(("gui", "Application"), ("doc", "Documentation"))

class Branch(models.Model):
    name = models.CharField(max_length=90, unique=True)
    path = models.CharField(max_length=90, unique=True)
    
    def __unicode__(self): return self.name

class Module(models.Model):
    name = models.CharField(max_length=90)
    branch = models.ForeignKey(Branch)
    type = models.CharField(max_length=9, choices=TYPES)
    
    def __unicode__(self): return self.name
    
    def templatePath(self):
        return join(self.branch.path,
                    messagePath(self.type, True),
                    self.name)
    def poPath(self):
        return join(self.branch.path,
                    messagePath(self.type, False),
                    self.name)

class Translator(models.Model):
    firstname = models.CharField(max_length=150)
    lastname = models.CharField(max_length=150)
    email = models.CharField(max_length=150)
    
    def __unicode__(self): return "%s %s" % (self.firstname, self.lastname)

class PofileManager(models.Manager):
    def gui(self):
        return self.get_query_set().filter(type="gui")

    def doc(self):
        return self.get_query_set().filter(type="doc")

class Pofile(models.Model):
    name = models.CharField(max_length=180)
    module = models.ForeignKey(Module)
    translator = models.ForeignKey(Translator, null=True)
    startdate = models.DateField(null=True)
    md5sum = models.CharField(max_length=180, blank=True, null=True)
    error = models.IntegerField(default=0)
    untranslated = models.IntegerField(default=0)
    fuzzy = models.IntegerField(default=0)
    translated = models.IntegerField(default=0)
    type = models.CharField(max_length=9, choices=TYPES)
    
    objects=PofileManager() # Custom manager
    
    def __unicode__(self): return self.name

    def total(self):
        return self.untranslated+self.fuzzy+self.translated

    def isPot(self):
        if self.translated+self.fuzzy==0:
            return True
        else:
            return False

    def isGui(self):
        if self.type=="gui":
            return True
        else:
            return False
    
    def isDoc(self):
        return not self.isGui()

    def suffix(self):
        if self.isPot():
            return ".pot"
        else:
            return ".po"

    def path(self):
        return join(self.module.branch.path,
                    messagePath(self.type, self.isPot()),
                    self.module.name,
                    self.name+self.suffix())

    def filePath(self):
        return join(settings.PY10N_FILE_BASEPATH, self.path())

    def webPath(self):
        return "http://websvn.kde.org/*checkout*/"+self.path()


    
    def getCss(self):
        # Move this outside models ?
        if self.isPot():
            css="untranslated"
        elif self.untranslated==0 and self.fuzzy==0:
            if self.errortho!=0:
                css="translated hasPologyErrors"
            else:
                css="translated"
        else:
            css="partial"
        return css

admin.site.register(Branch)
admin.site.register(Module)
admin.site.register(Translator)
admin.site.register(Pofile)