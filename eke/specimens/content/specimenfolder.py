# encoding: utf-8
# Copyright 2010 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''Specimen folder: content implementation.'''

from eke.specimens import ProjectMessageFactory as _
from eke.specimens.config import PROJECTNAME
from eke.specimens.interfaces import ISpecimenFolder
from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from zope.interface import implements

SpecimenFolderSchema = folder.ATFolderSchema.copy() + atapi.Schema((
    atapi.BooleanField(
        'showReferenceSets',
        default=True,
        storage=atapi.AnnotationStorage(),
        widget=atapi.BooleanWidget(
            label=_(u'Show Reference Sets'),
            description=_(u'True if a link to a part of the portal containing specimen reference sets should be displayed.'),
        ),
    ),
    atapi.BooleanField(
        'showERNELink',
        default=True,
        storage=atapi.AnnotationStorage(),
        widget=atapi.BooleanWidget(
            label=_(u'Show ERNE Link'),
            description=_(u'True if a link to the ERNE user interface should be displayed.'),
        ),
    ),
))
SpecimenFolderSchema['title'].storage = atapi.AnnotationStorage()

finalizeATCTSchema(SpecimenFolderSchema, folderish=True, moveDiscussion=False)

class SpecimenFolder(folder.ATFolder):
    '''Specimen folder which contains specimens.'''
    implements(ISpecimenFolder)
    portal_type       = 'Specimen Folder'
    schema            = SpecimenFolderSchema
    title             = atapi.ATFieldProperty('title')
    description       = atapi.ATFieldProperty('description')
    showReferenceSets = atapi.ATFieldProperty('showReferenceSets')
    showERNELink      = atapi.ATFieldProperty('showERNELink')
    

atapi.registerType(SpecimenFolder, PROJECTNAME)
