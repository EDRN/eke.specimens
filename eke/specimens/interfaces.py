# encoding: utf-8
# Copyright 2010 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''EDRN Knowledge Environment Specimens: interfaces.
'''

from eke.site.interfaces import ISite
from eke.study.interfaces import IProtocol

from eke.specimens import ProjectMessageFactory as _

from zope import schema
from zope.app.container.constraints import contains
from zope.interface import Interface

class ICaseControlSubset(Interface):
    '''A subset of participants who might be either disease-positive (case) or disease-negative (control).'''
    title = schema.TextLine(
        title=_(u'Title'),
        description=_(u'The name of this case/control subset.'),
        required=True,
    )
    description = schema.Text(
        title=_(u'Description'),
        description=_(u'An optional, short summary of this case/control subset.'),
        required=False,
    )
    subsetType = schema.TextLine(
        title=_(u'Subset Type'),
        description=_(u'Either "Case" or "Control"'),
        required=True,
    )
    def getNumParticipants():
        '''Tells how many participants provided specimens in this subset.'''

class ISpecimenStatistics(Interface):
    '''Contains specimen statistics, such as specimen count.'''
    # specimenCount = schema.Int(
    #     title=_(u'Specimen Count'),
    #     description=_(u'The number of specimens.'),
    #     required=False,
    #     default=0,
    #     min=0
    # )
    def getTotalNumSpecimens():
        '''Tells the total number of specimens in this collection.'''

class IStoredSpecimens(Interface):
    '''A mix-in interface that provides a schema field for the specimen storage type.'''
    def getStorageType():
        '''Tell how specimens are stored.'''


class ITextuallyEnhanced(Interface):
    '''A mix-in interface that provides a schema field for additional rich text.'''
    text = schema.Text(
        title=_(u'Body Text'),
        description=_(u'Additional richly-formatted text to display.'),
        required=False,
    )
    

class ISpecimenSystemFolder(ITextuallyEnhanced):
    '''Specimen system folder.'''
    contains('eke.specimens.interfaces.ISpecimenSystem')
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


class ISpecimenSystem(ITextuallyEnhanced, ISpecimenStatistics):
    '''Specimen system.'''
    contains('eke.specimens.interfaces.ISpecimenSet')
    title = schema.TextLine(
        title=_(u'Short Name'),
        description=_(u'A short identifier of this specimen system.'),
        required=True,
    )
    description = schema.Text(
        title=_(u'Description'),
        description=_(u'A short summary of this collection.'),
        required=False,
    )
    
class IERNESpecimenSystem(ISpecimenSystem):
    '''ERNE Specimen System'''
    contains('eke.specimens.interfaces.IERNESpecimenSet')


# class ISpecimenSet(ISpecimenStatistics):
class ISpecimenSet(ITextuallyEnhanced, ISpecimenStatistics):
    '''Abstract set of specimens'''
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
    # systemName: computed
    protocol = schema.Object(
        title=_(u'Protocol'),
        description=_(u'The single protocol that guided collection of specimens in this set.'),
        required=True,
        schema=IProtocol
    )

    
class IGenericSpecimenSet(ISpecimenSet, IStoredSpecimens):
    '''A generic set of specimens, such as a reference set or a PRoBE set.'''
    contains(
        'eke.specimens.interfaces.ICaseControlSubset'
        'Products.ATContentTypes.interfaces.IATFile',
        'Products.ATContentTypes.interfaces.IATLink'
    )
    fullName = schema.TextLine(
        title=_(u'Full Name'),
        description=_(u'Complete title for this specimen set.'),
        required=False,
    )
    cancerLocations = schema.List(
        title=_(u'Cancer Locations'),
        description=_(u'List (one per line) of the locations where cancer was detected.'),
        required=False,
        value_type=schema.TextLine(
            title=_(u'Cancer Location'),
            description=_(u'Location where cancer was detected.')
        )
    )
    collectionType = schema.List(
        title=_(u'Collection Types'),
        description=_(u'What kinds of specimens were collected from participants.'),
        required=False,
        value_type=schema.TextLine(
            title=_(u'Collection Type'),
            description=_(u'What kind of specimen was collected from the participant.')
        ),
    )
    def getNumParticipants():
        '''Tell how many participants provided specimens in this set.'''
    def getNumCases():
        '''Tell how many participants were in the case subset.'''
    def getNumControls():
        '''Tell how many participants were in the control subset.'''

class IERNESpecimenSet(ISpecimenSet):
    '''A set of specimens that comes from the EDRN Resource Network Exchange.'''
    site = schema.Object(
        title=_(u'Site'),
        description=_(u'Optional site at where these specimens are currently stored.'),
        required=False,
        schema=ISite
    )
    organs = schema.List(
        title=_(u'Organs'),
        description=_(u'Organs from which the specimens were sampled.'),
        required=False,
        value_type=schema.TextLine(
            title=_(u'Organ'),
            description=_(u'Organ from which the specimen was sampled.')
        )
    )
    collectionType = schema.TextLine(
        title=_(u'Collection Type'),
        description=_(u'What kind of specimen was collected from the participant.'),
        required=True
    )

class IInactiveERNESet(IERNESpecimenSet):
    '''A set of specimens from a former ERNE site.'''
    contains('eke.specimens.interfaces.IStoredInactiveSpecimen')
    contactName = schema.TextLine(
        title=_(u'Contact Name'),
        description=_(u'Name of the person to contact in order to obtain specimens from this set.'),
        required=False
    )

class IStoredInactiveSpecimen(IStoredSpecimens, ):
    title = schema.TextLine(
        title=_(u'Title'),
        description=_(u'The name of these stored specimens.'),
        required=True,
    )
    description = schema.Text(
        title=_(u'Description'),
        description=_(u'An optional summary or abstract of these stored specimens.'),
        required=False,
    )
    totalNumSpecimens = schema.Int(
        title=_(u'Number Stored'),
        description=_(u'Total number of specimens stored of this type.'),
        required=False,
        default=0,
        min=0
    )

# class ActiveERNE
# numParticipants = schema.Int(
#     title=_(u'Number of Participants'),
#     description=_(u'The total number of participants who provided specimens in this set.'),
#     required=False,
#     default=0,
#     min=0
# )


    # diagnosis = schema.TextLine(
    #     title=_(u'Diagnosis'),
    #     description=_(u'Diagnosis of participants with or without cancer.'),
    #     required=False,
    # )
    # siteName = schema.TextLine(
    #     title=_(u'Site Name'),
    #     description=_(u'Optional name of the site where these specimens are currently stored.'),
    #     required=False,
    # )
    # available = schema.Bool(
    #     title=_(u'Available'),
    #     description=_(u'Are the specimens in this set available for sharing?'),
    #     required=False,
    #     default=False,
    # )
    # contactEmail = schema.TextLine(
    #     title=_(u'Contact Email Address'),
    #     description=_(u'Email address of the contact name.'),
    #     required=False,
    # )
    # isERNE = schema.Bool(
    #     title=_(u'ERNE'),
    #     description=_(u'Is this an ERNE specimen set?'),
    #     required=False,
    # )
    # 