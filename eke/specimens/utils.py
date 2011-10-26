# encoding: utf-8
# Copyright 2011 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

from eea.facetednavigation.interfaces import ICriteria
from eea.facetednavigation.layout.interfaces import IFacetedLayout
from eke.specimens.interfaces import ISpecimenSet
from Products.CMFPlone.Portal import PloneSite
from zope.component import getMultiAdapter
from eke.specimens import STORAGE_VOCAB_NAME

def view(self):
    return super(PloneSite, self).view()

def patchMacrosDict(scope, original, replacement):
    scope.view.__dict__['macros'] = {}

def setFacetedNavigation(folder, request):
    subtyper = getMultiAdapter((folder, request), name=u'faceted_subtyper')
    if subtyper.is_faceted or not subtyper.can_enable: return
    subtyper.enable()
    criteria = ICriteria(folder)
    for cid in criteria.keys():
        criteria.delete(cid)
    criteria.add('resultsperpage', 'bottom', 'default', title='Results per page', hidden=True, start=0, end=50, step=5, default=20)
    criteria.add('sorting', 'bottom', 'default', title='Sort on', hidden=True, default='sortable_title')
    criteria.add(
        'checkbox', 'left', 'default',
        title='Collection',
        hidden=False,
        index='getCollectionName',
        operator='or',
        vocabulary=u'eke.specimens.CollectionNames',
        count=False,
        maxitems=0,
        sortreversed=False,
        hidezerocount=False,
    )
    criteria.add(
        'checkbox', 'bottom', 'default',
        title='Diagnosis',
        hidden=False,
        index='diagnosis',
        operator='or',
        vocabulary=u'eke.specimens.Diagnoses',
        count=False,
        maxitems=0,
        sortreversed=False,
        hidezerocount=False,
    )
    criteria.add(
        'checkbox', 'bottom', 'default',
        title='Storage',
        hidden=False,
        index='storageType',
        operator='or',
        vocabulary=STORAGE_VOCAB_NAME,
        count=False,
        maxitems=0,
        sortreversed=False,
        hidezerocount=False,
    )
    criteria.add(
        'checkbox', 'bottom', 'default',
        title='Obj provides',
        hidden=True,
        index='object_provides',
        operator='or',
        vocabulary=u'eea.faceted.vocabularies.ObjectProvides',
        default=[ISpecimenSet.__identifier__],
        count=False,
        maxitems=0,
        sortreversed=False,
        hidezerocount=False
    )
    criteria.add('debug', 'top', 'default', title='Debug Criteria', user='kelly')
    IFacetedLayout(folder).update_layout('faceted_specimens_view')
