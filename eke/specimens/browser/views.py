# encoding: utf-8
# Copyright 2010 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''
EDRN Knowledge Environment Specimens: views for content types.
'''

from Acquisition import aq_inner
from eke.specimens import STORAGE_VOCAB_NAME
from eke.specimens.interfaces import ISpecimenCollection, ISpecimenSet
from plone.memoize.instance import memoize
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

def getStorageTypeLabel(storageType, context):
    try:
        factory = getUtility(IVocabularyFactory, name=STORAGE_VOCAB_NAME)
        vocab = factory(context)
        return vocab.getTermByToken(storageType).title
    except LookupError:
        return u'?'


class SpecimenCollectionFolderView(BrowserView):
    '''Default view of a Specimen collection folder.'''
    __call__ = ViewPageTemplateFile('templates/specimencollectionfolder.pt')
    def haveSpecimenCollections(self):
        return len(self.specimenCollections()) > 0
    @memoize
    def specimenCollections(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        results = catalog(
            object_provides=ISpecimenCollection.__identifier__,
            path=dict(query='/'.join(context.getPhysicalPath()), depth=1),
            sort_on='sortable_title'
        )
        return [dict(title=i.Title, description=i.Description, specimenCount=i.specimenCount, url=i.getURL()) for i in results]
    def getStorageTypeLabel(self, storageType):
        context = aq_inner(self.context)
        return getStorageTypeLabel(storageType, context)


class SpecimenCollectionView(BrowserView):
    '''Default view of a Specimen Collection.'''
    __call__ = ViewPageTemplateFile('templates/specimencollection.pt')
    def haveSpecimenSets(self):
        return len(self.specimenSets()) > 0
    @memoize
    def specimenSets(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        results = catalog(
            object_provides=ISpecimenSet.__identifier__,
            path=dict(query='/'.join(context.getPhysicalPath()), depth=1),
            sort_on='sortable_title'
        )
        return [dict(title=i.Title, description=i.Description, specimenCount=i.specimenCount, url=i.getURL()) for i in results]

class SpecimenSetView(BrowserView):
    '''Default view of a Specimen Set.'''
    __call__ = ViewPageTemplateFile('templates/specimenset.pt')
    @memoize
    def storageTypeLabel(self):
        context = aq_inner(self.context)
        return getStorageTypeLabel(context.storageType, context)

