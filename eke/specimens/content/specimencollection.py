# encoding: utf-8
# Copyright 2010-2011 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''Specimen collection: content implementation.'''

from base import CountsSchema
from eke.specimens import ProjectMessageFactory as _
from eke.specimens.config import PROJECTNAME
from eke.specimens.interfaces import ISpecimenCollection, ISpecimenSet
from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.CMFCore.utils import getToolByName
from zope.interface import implements

SpecimenCollectionSchema = folder.ATFolderSchema.copy() + CountsSchema.copy() + atapi.Schema((
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
))
SpecimenCollectionSchema['title'].storage = atapi.AnnotationStorage()
SpecimenCollectionSchema['description'].storage = atapi.AnnotationStorage()
SpecimenCollectionSchema['specimenCount'].modes = ('view',)
SpecimenCollectionSchema['specimenCount'].widget.visible = {'edit': 'invisible', 'view': 'invisible'}

finalizeATCTSchema(SpecimenCollectionSchema, folderish=True, moveDiscussion=False)

class SpecimenCollection(folder.ATFolder):
    '''Specimen collection which contains sets of specimens.'''
    implements(ISpecimenCollection)
    portal_type       = 'Specimen Collection'
    schema            = SpecimenCollectionSchema
    title             = atapi.ATFieldProperty('title')
    description       = atapi.ATFieldProperty('description')
    text              = atapi.ATFieldProperty('text')
    specimenCount     = atapi.ATFieldProperty('specimenCount')

atapi.registerType(SpecimenCollection, PROJECTNAME)

def updateSpecimenCount(context, event):
    '''Update specimen count of collection from the sets it contains'''
    if not ISpecimenCollection.providedBy(context): return
    factory = getToolByName(context, 'portal_factory')
    if factory.isTemporary(context): return
    catalog = getToolByName(context, 'portal_catalog')
    brains = catalog(path=dict(query='/'.join(context.getPhysicalPath()), depth=1), object_provides=ISpecimenSet.__identifier__)
    context.specimenCount = sum([int(i.specimenCount) for i in brains])
    context.reindexObject(idxs=['specimenCount'])
