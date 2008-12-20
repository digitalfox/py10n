# -*- coding: UTF-8 -*-

# Sébastien Renard (sebastien.renard@digitalfox.org)
# Code licensed under GNU GPL V2

from datetime import datetime

from django.template.loader import get_template
from django.template import Context
from django.db.models import Q

from py10n.dj10n.models import Branch, Pofile, Translator
from py10n.settings import PY10N_NAME, PY10N_MAIL

def bookingPage(type="gui"):
    template=get_template("dj10n/pofiles.html")
    branches={}
    for branch in Branch.objects.filter(module__pk__isnull=False).distinct():
        branches[branch]=branch.module_set.filter(type=type).filter(pofile__pk__isnull=False).distinct()

    contexte=Context({"name" : PY10N_NAME,
                       "mail" : PY10N_MAIL,
                       "branches" : branches,
                       "type" : type })
    return template.render(contexte)
    
def translatorsPage(type="gui"):
    template=get_template("dj10n/translators.html")
    translators={}
    for translator in Translator.objects.filter(pofile__pk__isnull=False).distinct():
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
    contexte=Context({"name" : PY10N_NAME,
                       "mail" : PY10N_MAIL,
                       "translators" : translators,
                       "orphan_pos" : Pofile.objects.filter(translator=None).filter(type=type),
                       "type" : type
                       })
    return template.render(contexte)

def statsPage(type="gui"):
    template=get_template("dj10n/stats.html")
    # Non empty branches
    branches=[b for b in Branch.objects.all() if b.module_set.count()!=0]

    # Base query used to build stats - indicators are explainted below
    pos=Pofile.objects.filter(type=type)
    pos_completed=pos.filter(fuzzy=0).filter(untranslated=0)
    pos_perfect=pos_completed.filter(error=0)

    # Po number stat array
    # Each rows have branch name and the following indicators
    #    -  Total number of pofiles
    #     - Number of fully translated without fuzzy
    #     - Number of completed files without errors
    poNumber=[]

    # po number stats for all branch
    poNumber.append(["all", pos.count(), pos_completed.count(), pos_perfect.count()])


    # Same indicators for each branch
    for branch in branches:
        stat=[branch.name]
        stat.append(pos.filter(module__branch=branch).count())
        stat.append(pos_completed.filter(module__branch=branch).count())
        stat.append(pos_perfect.filter(module__branch=branch).count())
        poNumber.append(stat)

    # Some stats about translators
    # Each row is composed of indicator name and its value
    translators=Translator.objects.filter(pofile__type=type).distinct()
    activePos=pos.exclude(translator=None)
    translatorsStat=[]
    translatorsStat.append(["Traducteurs inscrits", translators.count()])
    translatorsStat.append(["Traducteurs actifs", translators.filter(pofile__pk__isnull=False).distinct().count()])
    translatorsStat.append(["Nombre moyen de fichiers gérés par traducteur", activePos.count()/translators.count()])
    translatorsStat.append(["Nombre moyen de messages gérés par traducteur",
                            sum([p.total() for p in activePos])/translators.count()])
    translatorsStat.append(["Nombre moyen de messages à traduire par traducteur",
                            sum([p.untranslated+p.fuzzy for p in activePos])/translators.count()])

    # To PO that need works in core KDE modules
    urgentPo=Pofile.objects.filter(module__urgent=True)
    urgentPo=urgentPo.filter(~Q(untranslated=0) | ~Q(fuzzy=0)).order_by("untranslated", "fuzzy").reverse() # That need word
    urgentPo=urgentPo[0:20] # 20 most urgent

    contexte=Context({"name" : PY10N_NAME,
                       "mail" : PY10N_MAIL,
                       "branches" : [b.name for b in branches]+["all"],
                       "poNumber" : poNumber,
                       "translatorsStat": translatorsStat,
                       "urgentPo" : urgentPo,
                       "type" : type
                       })
    return template.render(contexte)