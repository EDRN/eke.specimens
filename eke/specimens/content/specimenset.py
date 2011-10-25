# encoding: utf-8
# Copyright 2010-2011 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''Specimen set: content implementation.'''

from Acquisition import aq_inner, aq_parent
from base import CountsSchema
from eke.specimens import ProjectMessageFactory as _
from eke.specimens import STORAGE_VOCAB_NAME
from eke.specimens.config import PROJECTNAME
from eke.specimens.interfaces import ISpecimenSet
from Products.Archetypes import atapi
from Products.Archetypes.interfaces import IObjectPostValidation
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from zope.component import adapts
from zope.interface import implements

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
    atapi.StringField(
        'storageType',
        enforceVocabulary=True,
        required=True,
        storage=atapi.AnnotationStorage(),
        vocabulary_display_path_bound=-1,
        vocabulary_factory=STORAGE_VOCAB_NAME,
        widget=atapi.SelectionWidget(
            label=_(u'Storage Type'),
            description=_(u'How the specimens were processed and stored from these participants.'),
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
    atapi.BooleanField(
        'available',
        storage=atapi.AnnotationStorage(),
        required=False,
        widget=atapi.BooleanWidget(
            label=_(u'Available'),
            description=_(u'Are the specimens in this set available for sharing?'),
        ),
    ),
    atapi.StringField(
        'contactName',
        storage=atapi.AnnotationStorage(),
        required=False,
        widget=atapi.StringWidget(
            label=_(u'Contact Name'),
            description=_(u'Name of the person to contact in order to obtain specimens from this set.'),
        ),
    ),
    atapi.StringField(
        'contactEmail',
        storage=atapi.AnnotationStorage(),
        required=False,
        validators=('isEmail',),
        widget=atapi.StringWidget(
            label=_(u'Contact Email Address'),
            description=_(u'Email address of the contact name.'),
        ),
    ),
    atapi.ComputedField(
        'collectionName',
        required=False,
        searchable=True,
        expression='context._computeCollectionName()',
        multiValued=False,
        modes=('view',),
        widget=atapi.ComputedWidget(
            visible={'edit': 'invisible', 'view': 'invisible'},
        )
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
    storageType    = atapi.ATFieldProperty('storageType')
    specimenCount  = atapi.ATFieldProperty('specimenCount')
    numberCases    = atapi.ATFieldProperty('numberCases')
    numberControls = atapi.ATFieldProperty('numberControls')
    protocol       = atapi.ATReferenceFieldProperty('protocol')
    available      = atapi.ATFieldProperty('available')
    contactName    = atapi.ATFieldProperty('contactName')
    contactEmail   = atapi.ATFieldProperty('contactEmail')
    def _computeCollectionName(self):
        collection = aq_parent(aq_inner(self))
        if collection is not None:
            name = collection.title
            if name: return name
        return ''

atapi.registerType(SpecimenSet, PROJECTNAME)

class ContactInformationValidator(object):
    '''Ensures that contact information is provided if a specimen set is available for sharing.'''
    implements(IObjectPostValidation)
    adapts(ISpecimenSet)
    def __init__(self, context):
        self.context = context
    def _getValueFromRequest(self, request, field):
        return request.form.get(field, request.get(field, None))
    def __call__(self, request):
        isAvailable = self._getValueFromRequest(request, 'available')
        if isAvailable:
            for field in ('contactName', 'contactEmail'):
                value = self._getValueFromRequest(request, field)
                if not value: return {
                    field: _(u'A contact name and email address is required when specimens are available for sharing.')
                }
        return None
    
