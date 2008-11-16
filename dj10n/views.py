# -*- coding: UTF-8 -*-

# Sébastien Renard (sebastien.renard@digitalfox.org)
# Code licensed under GNU GPL V2


from django.template.loader import get_template
from django.template import Context

from py10n.dj10n.models import Branch, Pofile, Translator

#TODO: move that in settings
NAME="Sébastien Renard"
MAIL="Sebastien.Renard&#64;digitalfox.org"

def bookingPage(type="gui"):
    template=get_template("dj10n/wip-apps.php")
    contexte=Context({"name" : NAME,
                       "mail" : MAIL,
                       "branches" : Branch.objects.all(),
                       "type": type })
    return template.render(contexte)
    
def translatorsPage(type="gui"):
    template=get_template("dj10n/wip-translator.php")
    activeTranslators_id=Pofile.objects.exclude(translator__exact=None).values_list('translator', flat=True).distinct()
    contexte=Context({"name" : NAME,
                       "mail" : MAIL,
                       "translators" : Translator.objects.filter(id__in=activeTranslators_id),
                       "orphan_pos" : Pofile.objects.filter(translator=None),
                       "type": type })
    return template.render(contexte)
