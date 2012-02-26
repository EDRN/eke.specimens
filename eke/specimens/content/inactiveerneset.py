# encoding: utf-8
# Copyright 2012 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''Inactive ERNE Set: content implementation'''

from base import ERNESpecimenSet, ERNESpecimenSetSchema
from eke.specimens import ProjectMessageFactory as _
from eke.specimens.config import PROJECTNAME
from eke.specimens.interfaces import IInactiveERNESet, IInactiveStoredSpecimens
from Products.Archetypes import atapi
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.CMFCore.utils import getToolByName
from zope.interface import implements

InactiveERNESetSchema = ERNESpecimenSetSchema.copy() + atapi.Schema((
    atapi.StringField(
        'contactName',
        required=False,
        storage=atapi.AnnotationStorage(),
        searchable=True,
        widget=atapi.StringWidget(
            label=_(u'Contact Name'),
            description=_(u'Name of the person to contact in order to obtain specimens from this set'),
        ),
    ),
    atapi.ComputedField(
        'storageType',
        expression='context._computeStorageTypes()',
        widget=atapi.ComputedWidget(
            label=_(u'Storage Types'),
            description=_(u'The ways in which specimens in this set are stored.'),
        ),
    ),
    atapi.ComputedField(
        'totalNumSpecimens',
        expression='context._computeTotalNumSpecimens()',
        widget=atapi.ComputedWidget(
            label=_(u'Specimens'),
            description=_(u'Total number of specimens stored.'),
        ),
    ),
))

finalizeATCTSchema(InactiveERNESetSchema, folderish=True, moveDiscussion=True)

class InactiveERNESet(ERNESpecimenSet):
    '''A set of specimens from an inactive ERNE site.'''
    implements(IInactiveERNESet)
    portal_type   = 'Inactive ERNE Set'
    schema        = InactiveERNESetSchema
    contactName = atapi.ATFieldProperty('contactName')
    def _computeStorageTypes(self):
        factory = getToolByName(self, 'portal_factory')
        if factory.isTemporary(self): return tuple()
        catalog = getToolByName(self, 'portal_catalog')
        brains = catalog(
            path=dict(query='/'.join(self.getPhysicalPath()), depth=1),
            object_provides=IInactiveStoredSpecimens.__identifier__,
            sort_on='getStorageType',
        )
        return [i.getStorageType for i in brains]
    def _computeTotalNumSpecimens(self):
        factory = getToolByName(self, 'portal_factory')
        if factory.isTemporary(self): return tuple()
        catalog = getToolByName(self, 'portal_catalog')
        brains = catalog(
            path=dict(query='/'.join(self.getPhysicalPath()), depth=1),
            object_provides=IInactiveStoredSpecimens.__identifier__,
            sort_on='getStorageType',
        )
        return sum([int(i.getTotalNumSpecimens) for i in brains])

atapi.registerType(InactiveERNESet, PROJECTNAME)
