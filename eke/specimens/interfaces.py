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

class ISpecimenStatistics(Interface):
    '''Contains specimen statistics, such as specimen count.'''
    specimenCount = schema.Int(
        title=_(u'Specimen Count'),
        description=_(u'The number of specimens.'),
        required=False,
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
        required=False,
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
    organs = schema.List(
        title=_(u'Organs'),
        description=_(u'Names of the organs from which specimens were taken.'),
        required=False,
        value_type=schema.TextLine(
            title=_(u'Organ'),
            description=_(u'Name of an organ from which specimens were taken.'),
        )
    )
    diagnosis = schema.TextLine(
        title=_(u'Diagnosis'),
        description=_(u'Diagnosis of participants with or without cancer.'),
        required=False,
    )
    protocol = schema.Object(
        title=_(u'Protocol'),
        description=_(u'The single protocol that guided collection of specimens in this set.'),
        required=True,
        schema=IProtocol
    )
    site = schema.Object(
        title=_(u'Site'),
        description=_(u'Optional site at where these specimens are currently stored.'),
        required=False,
        schema=ISite
    )
    siteName = schema.TextLine(
        title=_(u'Site Name'),
        description=_(u'Optional name of the site where these specimens are currently stored.'),
        required=False,
    )
    available = schema.Bool(
        title=_(u'Available'),
        description=_(u'Are the specimens in this set available for sharing?'),
        required=False,
        default=False,
    )
    contactName = schema.TextLine(
        title=_(u'Contact Name'),
        description=_(u'Name of the person to contact in order to obtain specimens from this set.'),
        required=False
    )
    contactEmail = schema.TextLine(
        title=_(u'Contact Email Address'),
        description=_(u'Email address of the contact name.'),
        required=False,
    )
    isERNE = schema.Bool(
        title=_(u'ERNE'),
        description=_(u'Is this an ERNE specimen set?'),
        required=False,
    )
    