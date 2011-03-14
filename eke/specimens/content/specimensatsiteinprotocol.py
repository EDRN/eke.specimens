# encoding: utf-8
# Copyright 2010 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''Specimens at a single site and collected by various protocols: content implementation.'''

from base import CountsSchema
from eke.specimens import ProjectMessageFactory as _
from eke.specimens.config import PROJECTNAME
from eke.specimens.interfaces import ISpecimensAtSiteInProtocol, ISpecimensInProtocol, IUpdatable
from Products.Archetypes import atapi
from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.CMFCore.utils import getToolByName
from zope.interface import implements

SpecimensAtSiteInProtocolSchema = ATFolder.schema.copy() + CountsSchema.copy() + atapi.Schema((
    atapi.ComputedField(
        'title',
        accessor='Title',
        searchable=True,
        expression='context._computeSiteTitle()',
        modes=('view',),
        widget=atapi.ComputedWidget(
            visible={'edit': 'invisible', 'view': 'invisible'},
        ),
    ),
    atapi.ReferenceField(
        'site',
        required=True,
        enforceVocabulary=True,
        multiValued=False,
        searchable=True,
        storage=atapi.AnnotationStorage(),
        relationship='siteThatCollectedSpecimens',
        vocabulary_display_path_bound=-1,
        vocabulary_factory=u'eke.site.Sites',
        widget=atapi.ReferenceWidget(
            label=_(u'Site'),
            description=_(u"The site that collected specimens under various protocols' guidance."),
        ),
    ),
))
SpecimensAtSiteInProtocolSchema['description'].widget.visible = {'edit': 'invisible', 'view': 'invisible'}

finalizeATCTSchema(SpecimensAtSiteInProtocolSchema, folderish=True, moveDiscussion=False)

class SpecimensAtSiteInProtocol(ATFolder):
    '''Specimens at a site'''
    implements(ISpecimensAtSiteInProtocol, IUpdatable)
    portal_type      = 'Specimens at Site in Protocol'
    schema           = SpecimensAtSiteInProtocolSchema
    participantCount = atapi.ATFieldProperty('participantCount')
    site             = atapi.ATReferenceFieldProperty('site')
    specimenCount    = atapi.ATFieldProperty('specimenCount')
    def _computeSiteTitle(self):
        return self.site is not None and self.site.title or _(u'Unknown Site')
    def updateCounts(self):
        specimens = participants = 0
        try:
            catalog = getToolByName(self, 'portal_catalog')
            mine = catalog(
                object_provides=ISpecimensInProtocol.__identifier__,
                path=dict(query='/'.join(self.getPhysicalPath()), depth=1),
            )
            counts = [(i.specimenCount, i.participantCount) for i in mine]
            if len(counts) == 0:
                self.specimenCount = self.participantCount = 0
                return
            specimens, participants = sum(zip(*counts)[0]), sum(zip(*counts)[1])
        except AttributeError:
            pass
        if specimens == participants == 0:
            children = self.objectIds()
            if len(children) == 0:
                self.specimenCount = self.participantCount = 0
                return
            counts = [(self[i].specimenCount, self[i].participantCount) for i in children]
            specimens, participants = sum(zip(*counts)[0]), sum(zip(*counts)[1])
        self.specimenCount, self.participantCount = specimens, participants
        self.reindexObject(idxs=['specimenCount', 'participantCount'])

atapi.registerType(SpecimensAtSiteInProtocol, PROJECTNAME)

def updateSpecimensAtSiteInProtocol(context, event):
    if IUpdatable.providedBy(context):
        context.updateCounts()
        context.reindexObject(idxs=['specimenCount', 'participantCount'])

