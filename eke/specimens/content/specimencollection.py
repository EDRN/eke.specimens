# encoding: utf-8
# Copyright 2010-2011 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''Specimen collection: content implementation.'''

from eke.specimens import ProjectMessageFactory as _
from eke.specimens.config import PROJECTNAME
from eke.specimens.interfaces import ISpecimenCollection
from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from zope.interface import implements
from base import CountsSchema

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
