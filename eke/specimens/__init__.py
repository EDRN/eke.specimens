# encoding: utf-8
# Copyright 2010–2012 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''EDRN Knowledge Environment Specimens: initialization.
'''

from zope.i18nmessageid import MessageFactory

ProjectMessageFactory = MessageFactory('eke.specimens')

STORAGE_VOCAB_NAME    = u'https://www.compass.fhcrc.org/edrns/cgi-bin/pilot/cde/CDEDetailed.asp?cdeid=529'
ORGAN_VOCAB_NAME      = u'https://www.compass.fhcrc.org/edrns/cgi-bin/pilot/cde/CDEDetailed.asp?cdeid=581'
COLLECTION_VOCAB_NAME = u'https://www.compass.fhcrc.org/edrns/cgi-bin/pilot/cde/CDEDetailed.asp?cdeid=524'

from eke.specimens import config
from Products.Archetypes import atapi
import Products.CMFCore

def initialize(context):
    '''Initializer called when used as a Zope 2 product.'''
    from content import (
        specimensystemfolder,
        specimensystem,
        genericspecimenset,
        casecontrolsubset,
        inactiveerneset,
        activeerneset,
        ernespecimensystem,
    ) # for lame side effect
    contentTypes, constructors, ftis = atapi.process_types(atapi.listTypes(config.PROJECTNAME), config.PROJECTNAME)
    for atype, constructor in zip(contentTypes, constructors):
        Products.CMFCore.utils.ContentInit(
            '%s: %s' % (config.PROJECTNAME, atype.portal_type),
            content_types=(atype,),
            permission=config.ADD_PERMISSIONS[atype.portal_type],
            extra_constructors=(constructor,)
        ).initialize(context)
    
