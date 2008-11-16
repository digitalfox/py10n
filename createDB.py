#!/usr/bin/python
# -*- coding: utf-8 -*-

# Sébastien Renard (sebastien.renard@digitalfox.org)
# Code licensed under GNU GPL V2

"""Py10n database creation script"""

## Setup django envt & django imports
from django.core.management import execute_manager, setup_environ
import settings
setup_environ(settings)

from py10n.dj10n.models import Branch

def main():
    # Sync db
    #execute_manager(settings, argv="syncdb")
    execute_manager(settings, argv=[__file__, "syncdb"])
    
    # Populate initial branch
    for name, path in (("trunk","trunk/l10n-kde4"), ("stable", "branches/stable/l10n-kde4")):
        Branch.objects.get_or_create(name=name, path=path)

    print
    print "Now, you can synchronise your database with 'py10n -sg' for GUI and 'py10n -sd' for docs"

if __name__ == "__main__":
    main()