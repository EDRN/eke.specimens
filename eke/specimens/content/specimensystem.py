# encoding: utf-8
# Copyright 2010–2012 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''Specimen system: content implementation.'''

# from base import CountsSchema
from eke.specimens import ProjectMessageFactory as _
from eke.specimens.config import PROJECTNAME
from eke.specimens.interfaces import ISpecimenSystem, ISpecimenSet
from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.CMFCore.utils import getToolByName
from zope.interface import implements

SpecimenSystemSchema = folder.ATFolderSchema.copy() + atapi.Schema(( # + CountsSchema.copy()
    atapi.TextField(
        'text',
        required=False,
        searchable=True,
        primary=True,
        storage=atapi.AnnotationStorage(),
        validators=('isTidyHtmlWithCleanup',),
        default_output_type='text/x-html-safe',
        widget=atapi.RichWidget(
            label=_(u'Body Text'),
            description=_(u'Full body text to display on this folder above its contents.'),
            rows=10,
            allow_file_upload=False,
        ),
    ),
    atapi.ComputedField(
        'totalNumSpecimens',
        searchable=False,
        expression='context._computeTotalNumSpecimens()',
        widget=atapi.ComputedWidget(
            label=_(u'Total Specimens'),
            description=_(u'The total number of specimens across all specimens sets in this system.'),
        ),
    ),
))
SpecimenSystemSchema['title'].storage = atapi.AnnotationStorage()
SpecimenSystemSchema['description'].storage = atapi.AnnotationStorage()
# SpecimenSystemSchema['specimenCount'].modes = ('view',)
# SpecimenSystemSchema['specimenCount'].widget.visible = {'edit': 'invisible', 'view': 'invisible'}

finalizeATCTSchema(SpecimenSystemSchema, folderish=True, moveDiscussion=False)

class SpecimenSystem(folder.ATFolder):
    '''Specimen system which contains sets of specimens.'''
    implements(ISpecimenSystem)
    portal_type       = 'Specimen System'
    schema            = SpecimenSystemSchema
    title             = atapi.ATFieldProperty('title')
    description       = atapi.ATFieldProperty('description')
    text              = atapi.ATFieldProperty('text')
    def _computeTotalNumSpecimens(self):
        factory = getToolByName(self, 'portal_factory')
        if factory.isTemporary(self): return 0
        catalog = getToolByName(self, 'portal_catalog')
        brains = catalog(path=dict(query='/'.join(self.getPhysicalPath()), depth=1), object_provides=ISpecimenSet.__identifier__)
        return sum([int(i.getTotalNumSpecimens) for i in brains])

atapi.registerType(SpecimenSystem, PROJECTNAME)

# def updateSpecimenCount(context, event):
#     '''Update specimen count of a Specimen System from the Specimen Sets it contains.'''
#     if not ISpecimenSystem.providedBy(context): return
#     factory = getToolByName(context, 'portal_factory')
#     if factory.isTemporary(context): return
#     catalog = getToolByName(context, 'portal_catalog')
#     brains = catalog(path=dict(query='/'.join(context.getPhysicalPath()), depth=1), object_provides=ISpecimenSet.__identifier__)
#     context.specimenCount = sum([int(i.specimenCount) for i in brains])
#     context.reindexObject(idxs=['specimenCount'])
