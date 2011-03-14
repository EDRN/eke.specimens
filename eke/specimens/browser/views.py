# encoding: utf-8
# Copyright 2010 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''
EDRN Knowledge Environment Specimens: views for content types.
'''

from Acquisition import aq_inner, aq_parent
from eke.knowledge.browser.views import KnowledgeFolderView
from eke.specimens import ProjectMessageFactory as _, STORAGE_VOCAB_NAME
from eke.specimens.interfaces import ISpecimensAtSiteInProtocol, ISpecimensInProtocol, ISpecimenRecord
from plone.memoize.instance import memoize
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from utils import getInventory, SITES
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
import urllib

class SpecimenFolderView(KnowledgeFolderView):
    '''Default view of a Specimen folder.'''
    __call__ = ViewPageTemplateFile('templates/specimenfolder.pt')
    def haveSpecimensAtSites(self):
        return self.totalSpecimens() > 0
    def specimenChartTag(self):
        specimenCounts = self.specimensAtSites()
        values = [i['specimenCount'] for i in specimenCounts]
        labels = u'|'.join(reversed([i['title'].strip() for i in specimenCounts]))
        data = u','.join([unicode(i) for i in values])
        size = u'600x%d' % (30 * len(specimenCounts)) # in pixels
        maximum = max(values)
        params = {
            'cht':  'bhs',                          # Type: bar, horizontal, stacked
            'chs':  size,                           # Size in pixels
            'chf':  'b0,lg,90,a90101,0,ffffff,1',   # Fill with gradients from white to "NCI Red"
            'chxt': 'x,y',                          # Show both X and Y axis labels
            'chxl': '1:|' + labels,                 # Labels on the X axis
            'chd':  't:' + data,                    # Counts of specimens for each bar
            'chxr': '0,0,%d' % maximum,             # 0 to top value on X axis
            'chds': '0,%d' % maximum,               # Data value limits
        }
        return u'<img src="http://chart.apis.google.com/chart?%s" alt="%s"/>' % (urllib.urlencode(params), _(u'Specimen Chart'))
    def totalSpecimens(self):
        return sum([i['specimenCount'] for i in self.specimensAtSites()])
    def totalParticipants(self):
        return sum([i['participantCount'] for i in self.specimensAtSites()])
    @memoize
    def specimensAtSites(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        results = catalog(
            object_provides=ISpecimensAtSiteInProtocol.__identifier__,
            path=dict(query='/'.join(context.getPhysicalPath()), depth=1),
            sort_on='sortable_title'
        )
        return [
            dict(title=i.Title, specimenCount=i.specimenCount, participantCount=i.participantCount, url=i.getURL())
            for i in results
        ]

class SpecimensAtSiteInProtocolView(BrowserView):
    '''Default view of a Specimens at Site in Protocol object.'''
    __call__ = ViewPageTemplateFile('templates/specimensatsiteinprotocol.pt')
    def haveSpecimensInProtocols(self):
        return len(self.specimensInProtocols()) > 0
    @memoize
    def specimensInProtocols(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        results = catalog(
            object_provides=ISpecimensInProtocol.__identifier__,
            path=dict(query='/'.join(context.getPhysicalPath()), depth=1),
            sort_on='sortable_title'
        )
        return [
            dict(title=i.Title, specimenCount=i.specimenCount, participantCount=i.participantCount, url=i.getURL())
            for i in results
        ]

class SpecimensInProtocolView(BrowserView):
    '''Default view of a Specimens in Protocol object.'''
    __call__ = ViewPageTemplateFile('templates/specimensinprotocol.pt')
    def haveSpecimenRecords(self):
        return len(self.specimenRecords()) > 0
    @memoize
    def specimenRecords(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        results = catalog(
            object_provides=ISpecimenRecord.__identifier__,
            path=dict(query='/'.join(context.getPhysicalPath()), depth=1),
        )
        return [dict(title=i.Title, url=i.getURL()) for i in results]

class SpecimenRecordView(BrowserView):
    '''Default view of a Specimen Record object.'''
    __call__ = ViewPageTemplateFile('templates/specimenrecord.pt')
    @memoize
    def specimens(self):
        context = aq_inner(self.context)
        sip = aq_parent(aq_inner(context))
        if not sip: return None
        sasip = aq_parent(aq_inner(sip))
        if not sasip: return None
        site = sasip.site
        if not site: return None
        siteID = site.identifier
        if not siteID: return None
        erneID = SITES.get(siteID, None)
        if not erneID: return None
        return getInventory(erneID, context.cancerDiagnosis == 'with', context.specimenType, context.storageType)
    def getStorageFor(self, storageCode):
        try:
            context = aq_inner(self.context)
            factory = getUtility(IVocabularyFactory, name=STORAGE_VOCAB_NAME)
            vocab = factory(context)
            return vocab.getTermByToken(storageCode).title
        except LookupError:
            return u'Unknown' # FIXME: Not i18n
