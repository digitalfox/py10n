# -*- coding: UTF-8 -*-

# Sébastien Renard (sebastien.renard@digitalfox.org)
# Code licensed under GNU GPL V2


from datetime import datetime

from django.template.loader import get_template
from django.template import Context

from py10n.dj10n.models import Branch, Pofile, Translator

#TODO: move that in settings
NAME="Sébastien Renard"
MAIL="Sebastien.Renard&#64;digitalfox.org"

def bookingPage(type="gui"):
    template=get_template("dj10n/pofiles.html")
    branches={}
    #TODO: find a better way to filter branch ?
    for branch in [b for b in Branch.objects.all() if b.module_set.count()!=0]:
        branches[branch]=branch.module_set.filter(type=type)

    contexte=Context({"name" : NAME,
                       "mail" : MAIL,
                       "branches" : branches,
                       "now" : datetime.now() })
    return template.render(contexte)
    
def translatorsPage(type="gui"):
    template=get_template("dj10n/translators.html")
    translators={}
    activeTranslators_id=Pofile.objects.exclude(translator__exact=None).values_list('translator', flat=True).distinct()
    for translator in Translator.objects.filter(id__in=activeTranslators_id):
        translators[translator]={}
        translators[translator]["pos"]=translator.pofile_set.filter(type=type)
        error=fuzzy=untranslated=translated=0
        for po in translators[translator]["pos"]:
            error+=po.error 
            fuzzy+=po.fuzzy
            untranslated+=po.untranslated
            translated+=po.translated
        translators[translator]["error"]=error
        translators[translator]["fuzzy"]=fuzzy
        translators[translator]["untranslated"]=untranslated
        translators[translator]["translated"]=translated
    contexte=Context({"name" : NAME,
                       "mail" : MAIL,
                       "translators" : translators,
                       "orphan_pos" : Pofile.objects.filter(translator=None).filter(type=type),
                       "now" : datetime.now()
                       })
    return template.render(contexte)
