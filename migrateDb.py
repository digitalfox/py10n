#!/usr/bin/python
# -*- coding: utf-8 -*-

# Sébastien Renard (sebastien.renard@digitalfox.org)
# Code licensed under GNU GPL V2

"""Py10n migration tool from old py10n database (trunk only)"""

## Setup django envt & django imports
from django.core.management import setup_environ
import settings
setup_environ(settings)

import MySQLdb

from py10n.dj10n.models import Branch, Pofile, Translator, Module

# Old database connection - change this to your old py10n database
HOST="localhost"
USER="kdegui"
PWD="kde6666"
DB="kdegui"

def getOldBooking():
    try:
        dbConnection=MySQLdb.connect(host=HOST,
                    user=USER,
                    passwd=PWD,
                    db=DB,
                    use_unicode=True)
    except Exception, e:
        print "Cannot connect to old database (%s)" % e

    cursor=dbConnection.cursor()

    sql="""select p.name, p.startDate, p.type, t.firstname, t.lastname, t.email, m.name
            from poFile p, Translator t, Module m
            where p.idTranslator=t.idTranslator and p.idModule=m.idModule"""

    cursor.execute(sql)
    return cursor.fetchall()

def main():
    trunk=Branch.objects.get(name="trunk")
    for bookingRecord in getOldBooking():
        poName, startDate, type, firstname, lastname, email, moduleName=bookingRecord
        if firstname=="-" and lastname=="-":
            translator=None
        else:
            translator, new=Translator.objects.get_or_create(firstname=firstname, lastname=lastname, email=email)
            if new:
                translator.save()
        module, new=Module.objects.get_or_create(name=moduleName, type=type)
        if new:
            module.branch=trunk
            module.save()
        try:
            p=Pofile.objects.filter(name=poName, type=type)[0]
            p.translator=translator
            p.module=module
            if startDate.count("/")==2:
                D, M, Y=startDate.split("/")
                p.startdate="%s-%s-%s" % (Y, M, D)
            else:
                p.startdate=None
            p.save()
        except IndexError:
            print "Po does not exist: %s" % poName
            continue

if __name__ == "__main__":
    main()
