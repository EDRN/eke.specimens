# encoding: utf-8
# Copyright 2010 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''A record of specimens collected.'''

from Acquisition import aq_inner, aq_parent
from base import CountsSchema
from eke.specimens import ProjectMessageFactory as _, STORAGE_VOCAB_NAME, SPECIMEN_TYPE_VOCAB_NAME
from eke.specimens.config import PROJECTNAME
from eke.specimens.interfaces import ISpecimenRecord
from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content.schemata import finalizeATCTSchema, ATContentTypeSchema
from zope.component import getUtility
from zope.interface import implements, directlyProvides
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary

SpecimenRecordSchema = ATContentTypeSchema.copy() + CountsSchema.copy() + atapi.Schema((
    atapi.ComputedField(
        'title',
        accessor='Title',
        searchable=True,
        expression='context._computeRecordTitle()',
        modes=('view',),
        widget=atapi.ComputedWidget(
            visible={'edit': 'invisible', 'view': 'invisible'},
        ),
    ),
    atapi.ComputedField(
        'description',
        accessor='Description',
        searchable=True,
        expression='context._computeRecordDescription()',
        modes=('view',),
        widget=atapi.ComputedWidget(
            visible={'edit': 'invisible', 'view': 'invisible'},
        ),
    ),
    atapi.StringField(
        'cancerDiagnosis',
        enforceVocabulary=True,
        required=True,
        storage=atapi.AnnotationStorage(),
        vocabulary_display_path_bound=-1,
        vocabulary_factory=u'eke.specimens.CancerDiagnosisVocabulary',
        widget=atapi.SelectionWidget(
            label=_(u'Cancer Diagnosis'),
            description=_(u'Did the participants who gave these specimens have cancer?'),
        ),
    ),
    atapi.StringField(
        'specimenType',
        enforceVocabulary=True,
        required=True,
        storage=atapi.AnnotationStorage(),
        vocabulary_display_path_bound=-1,
        vocabulary_factory=SPECIMEN_TYPE_VOCAB_NAME,
        widget=atapi.SelectionWidget(
            label=_(u'Specimen Type'),
            description=_(u'The type of specimen collected from the participants.'),
        ),
    ),
    atapi.StringField(
        'storageType',
        enforceVocabulary=True,
        required=True,
        storage=atapi.AnnotationStorage(),
        vocabulary_display_path_bound=-1,
        vocabulary_factory=STORAGE_VOCAB_NAME,
        widget=atapi.SelectionWidget(
            label=_(u'Storage Type'),
            description=_(u'How the specimens were processed and stored from these participants.'),
        ),
    ),
    atapi.ComputedField(
        'siteName',
        accessor='siteName',
        expression='context._computeSiteName()',
        modes=('view',),
        widget=atapi.ComputedWidget(
            visible={'edit': 'visible', 'view': 'invisible'},
        ),
    ),
))
SpecimenRecordSchema['specimenCount'].widget.visible    = {'edit': 'visible',   'view': 'visible'},
SpecimenRecordSchema['participantCount'].widget.visible = {'edit': 'visible',   'view': 'visible'},

finalizeATCTSchema(SpecimenRecordSchema, folderish=False, moveDiscussion=False)

class SpecimenRecord(base.ATCTContent):
    '''Specimen record.'''
    implements(ISpecimenRecord)
    portal_type               = 'Specimen Record'
    schema                    = SpecimenRecordSchema
    participantCount          = atapi.ATFieldProperty('participantCount')
    specimenCount             = atapi.ATFieldProperty('specimenCount')
    specimenType              = atapi.ATFieldProperty('specimenType')
    storageType               = atapi.ATFieldProperty('storageType')
    cancerDiagnosis           = atapi.ATFieldProperty('cancerDiagnosis')
    def _getSite(self):
        sip = aq_parent(aq_inner(self))
        if sip is not None:
            sasip = aq_parent(aq_inner(sip))
            if sasip is not None and sasip.site:
                return sasip.site
        return None
    def _computeSiteName(self):
        site = self._getSite()
        return site is not None and site.Title() or ''
    def _computeRecordDescription(self):
        "Collected at Dr Tongue's 3D Clinic from 46 participants diagnosed with cancer"
        # FIXME: Not i18n
        siteName = _(u'Unknown Site')
        site = self._getSite()
        if site: siteName = site.Title()
        return u'Collected at %(siteName)s from %(participantCount)d participants diagnosed %(with)s cancer.' % {
            'siteName': siteName,
            'participantCount': self.participantCount,
            'with': self.cancerDiagnosis,
        }
    def _computeRecordTitle(self):
        try:
            specimenTypeVocab = getUtility(IVocabularyFactory, name=SPECIMEN_TYPE_VOCAB_NAME)(self)
            specimenType = specimenTypeVocab.getTermByToken(self.specimenType).title
        except LookupError:
            specimenType = _(u'Unknown')
        try:
            storageTypeVocab = getUtility(IVocabularyFactory, name=STORAGE_VOCAB_NAME)(self)
            storageType = storageTypeVocab.getTermByToken(self.storageType).title
        except LookupError:
            storageType = _(u'Unknown')
        # FIXME: Not i18n
        siteName = _(u'Unknown Site')
        sip = aq_parent(aq_inner(self))
        if sip is not None:
            sasip = aq_parent(aq_inner(sip))
            if sasip is not None and sasip.site:
                siteName = sasip.site.abbreviation and sasip.site.abbreviation or sasip.site.Title() 
        return u'%(specimenCount)d %(specimenType)s/%(storageType)s Specimens at %(site)s from %(participantCount)d ' \
            '%(with)s Cancer' % {
            'specimenCount':    self.specimenCount,
            'specimenType':     specimenType,
            'storageType':      storageType,
            'participantCount': self.participantCount,
            'with':             self.cancerDiagnosis,
            'site':             siteName
        }

atapi.registerType(SpecimenRecord, PROJECTNAME)

def CancerDiagnosisVocabularyFactory(context):
    # FIXME: not i18n
    return SimpleVocabulary.fromItems(((u'With Cancer', 'with'), (u'Without Cancer', 'without')))
directlyProvides(CancerDiagnosisVocabularyFactory, IVocabularyFactory)
