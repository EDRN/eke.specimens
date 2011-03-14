# encoding: utf-8
# Copyright 2010 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''Specimens collected by a single protocol: content implementation.'''

from Acquisition import aq_inner, aq_parent
from base import CountsSchema
from eke.specimens import ProjectMessageFactory as _
from eke.specimens.config import PROJECTNAME
from eke.specimens.interfaces import ISpecimensInProtocol, IUpdatable, ISpecimenRecord
from Products.Archetypes import atapi
from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.CMFCore.utils import getToolByName
from zope.interface import implements

SpecimensInProtocolSchema = ATFolder.schema.copy() + CountsSchema.copy() + atapi.Schema((
    atapi.ComputedField(
        'title',
        accessor='Title',
        searchable=True,
        expression='context._computeProtocolTitle()',
        modes=('view',),
        widget=atapi.ComputedWidget(
            visible={'edit': 'invisible', 'view': 'invisible'},
        ),
    ),
    atapi.ReferenceField(
        'protocol',
        required=True,
        enforceVocabulary=True,
        multiValued=False,
        searchable=True,
        storage=atapi.AnnotationStorage(),
        relationship='protocolThatCollectedSpecimens',
        vocabulary_display_path_bound=-1,
        vocabulary_factory=u'eke.study.ProtocolsVocabulary',
        widget=atapi.ReferenceWidget(
            label=_(u'Protocol'),
            description=_(u'The single protocol that guided collection of various specimens.'),
        ),
    ),
))
SpecimensInProtocolSchema['description'].widget.visible = {'edit': 'invisible', 'view': 'invisible'}

finalizeATCTSchema(SpecimensInProtocolSchema, folderish=True, moveDiscussion=False)

class SpecimensInProtocol(ATFolder):
    '''Specimens in a protocol'''
    implements(ISpecimensInProtocol, IUpdatable)
    portal_type      = 'Specimens in Protocol'
    schema           = SpecimensInProtocolSchema
    participantCount = atapi.ATFieldProperty('participantCount')
    protocol         = atapi.ATReferenceFieldProperty('protocol')
    specimenCount    = atapi.ATFieldProperty('specimenCount')
    def _computeProtocolTitle(self):
        return self.protocol is not None and self.protocol.title or _(u'Unknown Protocol')
    def updateCounts(self):
        specimens = participants = 0
        try:
            catalog = getToolByName(self, 'portal_catalog')
            mine = catalog(
                object_provides=ISpecimenRecord.__identifier__,
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
        

atapi.registerType(SpecimensInProtocol, PROJECTNAME)

def updateSpecimensInProtocol(context, event):
    if IUpdatable.providedBy(context):
        context.updateCounts()
        context.reindexObject(idxs=['specimenCount', 'participantCount'])
        # Promulgate upward
        parent = context.aq_inner.aq_parent
        if IUpdatable.providedBy(parent):
            parent.updateCounts()

def handleNewSpecimenRecord(context, event):
    parent = aq_parent(aq_inner(context))
    if not parent:
        return
    for i in parent.objectIds():
        sr = parent[i]
        sr.reindexObject(idxs=['Title', 'identifier'])
