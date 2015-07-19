# -*- coding: utf-8 -*-
# Sébastien Renard (sebastien.renard@digitalfox.org)
# Code licensed under GNU GPL V2

"""Simple interface with Pology"""

from os.path import join
from os import popen
import settings

def posieve(sieve, options, target):
    """@param sieve: the sieve to be used
       @type sieve: str
       @options: list of (key, value) that will be give to pology as -skey:value
       """
    try:
        pologyPath=join(settings.PY10N_FILE_BASEPATH, "trunk/l10n-support/")
        optionsString=" ".join("-s%s:%s" % (k, v) for (k, v) in options)
        cmd="python %s/pology/scripts/posieve.py -b %s %s %s" % \
            (pologyPath, optionsString, sieve, target)
        process = popen(cmd)
        result = process.readlines()
        process.close()
        print "".join(result)
    except Exception, e:
        print "Cannot compute pology errors statistics. Error was : %s" % (e)
