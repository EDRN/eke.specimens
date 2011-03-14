# encoding: utf-8
# Copyright 2010 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''EDRN Knowledge Environment Specimens: ingest of specimen data.
'''

from Acquisition import aq_inner
from eke.site.interfaces import ISite
from eke.study.interfaces import IProtocol
from plone.i18n.normalizer.interfaces import IIDNormalizer
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from utils import getSpecimens, SITES
from zope.component import queryUtility

# ERNE protocol ID
_erneURI = 'http://edrn.nci.nih.gov/data/protocols/116'

class BadERNEProtocolException(Exception):
    def __init__(self, numFound=0):
        # TODO: Grrr. Exception is an old-style class in Python 2.4. In 2.5+, change
        # this to: super(BadERNEProtocolException, self).__init__('Require exactly one ERNE...)
        Exception.__init__(self, 'Require exactly one ERNE protocol, found "%d"' % numFound)

class SpecimenFolderIngestor(BrowserView):
    '''Ingest specimen data directly from the ERNE query interface.'''
    template = ViewPageTemplateFile('templates/ingestresults.pt')
    render = True
    def _getTools(self, context):
        '''Return a triple containing the catalog tool, the workflow tool, and a function that can be called
        to normalize object IDs.'''
        catalog, wfTool = getToolByName(context, 'portal_catalog'), getToolByName(context, 'portal_workflow')
        normalize = queryUtility(IIDNormalizer).normalize
        return catalog, wfTool, normalize
    def _doPublish(self, item, wfTool):
        '''Using the given workflow tool ``wfTool``, publish the given item, and all its children.'''
        try:
            wfTool.doActionFor(item, action='publish')
            item.reindexObject()
        except WorkflowException:
            pass
        for i in item.objectIds():
            subItem = item[i]
            self._doPublish(subItem, wfTool)
    def __call__(self):
        '''Do the ingest.'''
        log = []
        context = aq_inner(self.context)
        catalog, wfTool, normalize = self._getTools(context)
        
        # First, find the ERNE protocol.  All of the specimens in ERNE were gathered under the ERNE protocol.
        results = catalog(identifier=_erneURI, object_provides=IProtocol.__identifier__)
        if len(results) == 0:
            # No ERNE? No ingest.
            self.results = [u'No ERNE protocol (%s), so no specimen ingest' % _erneURI]
            return self.render and self.template() or None
        elif len(results) > 1:
            raise BadERNEProtocolException(len(results))
        erne = results[0].getObject()
        erneObjectID = normalize(erne.title)
        
        # Clear out everything so we start with a clean slate.
        context.manage_delObjects(context.objectIds())
        
        # For each site:
        for siteID, erneID in SITES.items():
            # Find the site.
            results = catalog(identifier=siteID, object_provides=ISite.__identifier__)
            if len(results) != 1:
                # Not found?  Skip it.  More than one?  Weird, but skip 'em.
                log.append('Exactly one site required for %s, but found %d; skipping' % (siteID, len(results)))
                continue
            site = results[0].getObject()
            
            # Create a SASIP to capture the site reference.
            sasip = context[context.invokeFactory('Specimens at Site in Protocol', normalize(site.Title()))]
            sasip.setSite(site)
            sasip.reindexObject()
            
            # Create a SIP to capture the protocol reference.
            sip = sasip[sasip.invokeFactory('Specimens in Protocol', erneObjectID)]
            sip.setProtocol(erne)
            sip.reindexObject()
            
            # Grab all the specimens at this site.
            statistics = getSpecimens(erneID)
            if len(statistics) == 0:
                # None?  We're done.
                log.append('Zero specimens returned for %s' % siteID)
                continue
            
            recordNum = totalSpecs = totalPpts = 0
            for s in statistics:
                recordNum += 1
                r = sip[sip.invokeFactory('Specimen Record', str(recordNum))]
                r.cancerDiagnosis, r.specimenType, r.storageType = s.withCancer == True and 'with' or 'without', s.kind, s.storage
                r.specimenCount, r.participantCount = s.numSpecs, s.numPpts
                totalSpecs, totalPpts = totalSpecs + s.numSpecs, totalPpts + s.numPpts
                r.reindexObject()
            log.append('Ingested %d specimens (from %d participants) for %s' % (totalSpecs, totalPpts, siteID))
            self._doPublish(sasip, wfTool)
        self.results = log
        return self.render and self.template() or None

