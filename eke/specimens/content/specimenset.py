# encoding: utf-8
# Copyright 2010-2011 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''Specimen set: content implementation.'''

from eke.specimens import ProjectMessageFactory as _
from eke.specimens.config import PROJECTNAME
from eke.specimens.interfaces import ISpecimenSet
from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from zope.interface import implements
from base import CountsSchema

SpecimenSetSchema = folder.ATFolderSchema.copy() + CountsSchema.copy() + atapi.Schema((
    atapi.StringField(
        'shortName',
        required=True,
        searchable=True,
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u'Short Name'),
            description=_(u'A brief name or simple identifier for this specimen set.'),
            size=12,
        ),
    ),
    atapi.IntegerField(
        'numberCases',
        required=True,
        searchable=False,
        storage=atapi.AnnotationStorage(),
        widget=atapi.IntegerWidget(
            label=_(u'Cases'),
            description=_(u'The number of participant cases from which specimens were drawn in this set.'),
        ),
    ),
    atapi.IntegerField(
        'numberControls',
        required=True,
        searchable=False,
        storage=atapi.AnnotationStorage(),
        widget=atapi.IntegerWidget(
            label=_(u'Controls'),
            description=_(u'The number of participant controls who provided specimens drawn in this set.'),
        ),
    ),
    atapi.ReferenceField(
        'protocol',
        storage=atapi.AnnotationStorage(),
        enforceVocabulary=True,
        multiValued=False,
        vocabulary_factory=u'eke.study.ProtocolsVocabulary',
        relationship='protocolProvidingSpecimens',
        vocabulary_display_path_bound=-1,
        widget=atapi.ReferenceWidget(
            label=_(u'Protocol'),
            description=_(u'The single protocol that guided collection of specimens in this set'),
        ),
    ),
))
SpecimenSetSchema['title'].storage = atapi.AnnotationStorage()
SpecimenSetSchema['description'].storage = atapi.AnnotationStorage()

finalizeATCTSchema(SpecimenSetSchema, folderish=True, moveDiscussion=False)

class SpecimenSet(folder.ATFolder):
    '''Specimen set which describes a single set of related specimens.'''
    implements(ISpecimenSet)
    portal_type    = 'Specimen Set'
    schema         = SpecimenSetSchema
    title          = atapi.ATFieldProperty('title')
    description    = atapi.ATFieldProperty('description')
    shortName      = atapi.ATFieldProperty('shortName')
    specimenCount  = atapi.ATFieldProperty('specimenCount')
    numberCases    = atapi.ATFieldProperty('numberCases')
    numberControls = atapi.ATFieldProperty('numberControls')
    protocol       = atapi.ATReferenceFieldProperty('protocol')

atapi.registerType(SpecimenSet, PROJECTNAME)
