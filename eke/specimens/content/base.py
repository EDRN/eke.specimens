# encoding: utf-8
# Copyright 2010 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''EDRN Knowledge Environment Specimens: content base implementations and common features.'''

from eke.specimens import ProjectMessageFactory as _
from Products.Archetypes import atapi
from zope.schema.interfaces import IVocabularyFactory
from eke.specimens.interfaces import ISpecimenSet
from zope.schema.vocabulary import SimpleVocabulary
from zope.interface import directlyProvides
from Products.CMFCore.utils import getToolByName

# FIXME: not i18n
_diagnoses = SimpleVocabulary.fromItems((
    ('With Cancer', 'With Cancer'),
    ('Without Cancer', 'Without Cancer'),
))

# Schema for ISpecimenStatistics: specimen count.
CountsSchema = atapi.Schema((
    atapi.IntegerField(
        'specimenCount',
        required=True,
        default=0,
        searchable=False,
        storage=atapi.AnnotationStorage(),
        widget=atapi.IntegerWidget(
            label=_(u'Specimen Count'),
            description=_(u'How many individual specimens have been collected.'),
            visible={'edit': 'visible', 'view': 'visible'},
        ),
    ),
))

def SpecimenCollectionNamesVocabularyFactory(context):
    catalog = getToolByName(context, 'portal_catalog')
    items = list(catalog.uniqueValuesFor('getCollectionName'))
    items.sort()
    return SimpleVocabulary.fromItems([(i, i) for i in items])
directlyProvides(SpecimenCollectionNamesVocabularyFactory, IVocabularyFactory)

def DiagnosesVocabularyFactory(context):
    return _diagnoses
directlyProvides(DiagnosesVocabularyFactory, IVocabularyFactory)

def SitesWithSpecimensVocabulary(context):
    catalog = getToolByName(context, 'portal_catalog')
    results = catalog(object_provides=ISpecimenSet.__identifier__)
    siteNames = set([i.siteName for i in results if i.siteName])
    siteNames = list(siteNames)
    siteNames.sort()
    return SimpleVocabulary.fromItems([(i, i) for i in siteNames])
directlyProvides(SitesWithSpecimensVocabulary, IVocabularyFactory)
