# encoding: utf-8
# Copyright 2010 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''EDRN Knowledge Environment Specimens: interfaces.
'''

from eke.site.interfaces import ISite
from eke.specimens import ProjectMessageFactory as _
from eke.study.interfaces import IProtocol
from zope import schema
from zope.app.container.constraints import contains
from zope.interface import Interface

class ICounted(Interface):
    '''Something that counts specimens and participants.'''
    specimenCount = schema.Int(
        title=_(u'Specimen Count'),
        description=_(u'How many specimens have been collected.'),
        required=True,
        min=0,
        default=0
    )
    participantCount = schema.Int(
        title=_(u'Participant Count'),
        description=_(u'How many participants gave those specimens.'),
        required=True,
        min=0,
        default=0
    )
    

class IUpdatable(Interface):
    '''Something whose specimen and participant counts can be updated'''
    def updateCounts():
        '''Update my specimen and participant counts based on available information'''
    

class ISpecimenFolder(Interface):
    '''Specimen folder.'''
    contains('eke.specimens.interfaces.ISpecimensAtSiteInProtocol')
    title = schema.TextLine(
        title=_(u'Title'),
        description=_(u'Title of this folder'),
        required=True,
    )
    description = schema.Text(
        title=_(u'Description'),
        description=_(u'A short summary of this folder.'),
        required=False,
    )
    showReferenceSets = schema.Bool(
        title=_(u'Show Reference Sets'),
        description=_(u'True if a link to a part of the portal containing specimen reference sets should be displayed.'),
        required=False,
        default=True
    )
    showERNELink = schema.Bool(
        title=_(u'Show ERNE Link'),
        description=_(u'True if a link to the ERNE user interface should be displayed.'),
        required=False,
        default=True
    )
    

class ISpecimensAtSiteInProtocol(ICounted):
    '''Specimens at a site'''
    contains('eke.specimens.interfaces.ISpecimensInProtocol')
    site = schema.Object(
        title=_(u'Site'),
        description=_(u"The site that collected specimens under various protocols' guidance."),
        required=True,
        schema=ISite
    )
    

class ISpecimensInProtocol(ICounted):
    '''Specimens.'''
    contains('eke.specimens.interfaces.ISpecimenRecord')
    protocol = schema.Object(
        title=_(u'Protocol'),
        description=_(u'The single protocol that guided collection of various specimens.'),
        required=True,
        schema=IProtocol
    )
    

class ISpecimenRecord(ICounted):
    '''A record of specimens collected of a single type.'''
    cancerDiagnosis = schema.TextLine(
        title=_(u'Cancer Diagnosis'),
        description=_(u'Did the participants who gave these specimens have cancer?'),
        required=True,
    )
    specimenType = schema.TextLine(
        title=_(u'Specimen Type'),
        description=_(u'The type of specimen collected from the participants.'),
        required=True,
    )
    storageType = schema.TextLine(
        title=_(u'Storage Type'),
        description=_(u'How the specimens were processed and stored from these participants.'),
        required=True,
    )
