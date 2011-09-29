# encoding: utf-8
# Copyright 2010 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''EDRN Knowledge Environment Specimens: interfaces.
'''

from eke.specimens import ProjectMessageFactory as _
from eke.study.interfaces import IProtocol
from zope import schema
from zope.app.container.constraints import contains
from zope.interface import Interface

class ISpecimenStatistics(Interface):
    '''Contains specimen statistics, such as specimen count.'''
    specimenCount = schema.Int(
        title=_(u'Specimen Count'),
        description=_(u'The number of specimens.'),
        required=True,
        default=0,
        min=0
    )
    

class ISpecimenCollectionFolder(Interface):
    '''Specimen collection folder.'''
    contains('eke.specimens.interfaces.ISpecimenCollection')
    title = schema.TextLine(
        title=_(u'Title'),
        description=_(u'Title of this folder.'),
        required=True,
    )
    description = schema.Text(
        title=_(u'Description'),
        description=_(u'A short summary of this folder.'),
        required=False,
    )
    text = schema.Text(
        title=_(u'Body Text'),
        description=_(u'Full body text to display on this folder above its contents.'),
        required=False,
    )


class ISpecimenCollection(ISpecimenStatistics):
    '''Specimen collection.'''
    contains('eke.specimens.interfaces.ISpecimenSet')
    title = schema.TextLine(
        title=_(u'Title'),
        description=_(u'Title of this collection.'),
        required=True,
    )
    description = schema.Text(
        title=_(u'Description'),
        description=_(u'A short summary of this collection.'),
        required=False,
    )
    text = schema.Text(
        title=_(u'Body Text'),
        description=_(u'Full body text to display on this collection above its contents.'),
        required=False,
    )
    
    
class ISpecimenSet(ISpecimenStatistics):
    '''Specimen set'''
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
    shortName = schema.TextLine(
        title=_(u'Short Name'),
        description=_(u'A brief name or simple identifier for this specimen set.'),
        required=True,
    )
    storageType = schema.TextLine(
        title=_(u'Storage Type'),
        description=_(u'How the specimens were processed and stored from these participants.'),
        required=True,
    )
    numberCases = schema.Int(
        title=_(u'Cases'),
        description=_(u'The number of participant cases from which specimens were drawn in this set.'),
        required=True,
        default=0,
        min=0
    )
    numberControls = schema.Int(
        title=_(u'Controls'),
        description=_(u'The number of participant controls who provided specimens drawn in this set.'),
        required=True,
        default=0,
        min=0
    )
    protocol = schema.Object(
        title=_(u'Protocol'),
        description=_(u'The single protocol that guided collection of specimens in this set.'),
        required=True,
        schema=IProtocol
    )
    