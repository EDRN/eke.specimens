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
        super(BadERNEProtocolException, self).__init__('Require exactly one ERNE protocol, found %d' % numFound)

class SpecimenCollectionFolderIngestor(BrowserView):
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
        erneProtocol = results[0].getObject()
        
        # Find the ERNE collection & start with blank slate
        if 'erne' not in context.keys():
            erne = context[context.invokeFactory('Specimen Collection', 'erne')]
            erne.setTitle(u'ERNE')
            erne.setDescription(u'EDRN Resource Network Exchange')
            erne.setText(u'<p>Specimens collected by present and former EDRN member sites.</p>')
            erne.reindexObject()
            log.append('Created the ERNE collection at %s' % erne.absolute_url())
        else:
            erne = context['erne']
            erne.manage_delObjects(erne.keys())
            log.append('Using the existing ERNE collection at %s' % erne.absolute_url())
        
        # For each site:
        for siteID, erneID in SITES.items():
            # Find the site.
            results = catalog(identifier=siteID, object_provides=ISite.__identifier__)
            if len(results) != 1:
                # Not found?  Skip it.  More than one?  Weird, but skip 'em.
                log.append('Exactly one site required for %s, but found %d; skipping' % (siteID, len(results)))
                continue
            site = results[0].getObject()
            siteAbbrevName = site.abbreviation if site.abbreviation else site.title
            
            # Grab summaries of all the specimens at this site.
            summaries = getSpecimens(erneID)
            if len(summaries) == 0:
                # None?  Done.  TODO: Should we clear out any old portal records?
                log.append('Zero specimens returned for %s' % siteID)
                continue
            
            # Create
            recordNum = 0
            for summary in summaries:
                recordNum += 1
                sid = '%s-%d' % (site.siteID, recordNum)
                s = erne[erne.invokeFactory('Specimen Set', sid)]
                s.setTitle(u'%s Set #%d' %(siteAbbrevName, recordNum))
                s.setDescription(u'Specimens at %s via ERNE.' % site.title)
                s.shortName      = sid
                s.specimenCount  = summary.specimenCount
                s.storageType    = summary.storageType
                s.numberCases    = summary.numberCases
                s.numberControls = summary.numberControls
                s.diagnosis      = u'With Cancer' if summary.diagnosis else u'Without Cancer'
                s.protocol       = erneProtocol
                s.site           = site
                s.siteName       = site.title
                if summary.available:
                    s.available    = True
                    s.contactName  = u'EDRN Site Specimen Bank Contact'
                    s.contactEmail = summary.contactEmail
                else:
                    s.available = False
                s.reindexObject()
            log.append('Created %d sets for site %s' % (recordNum, siteAbbrevName))
        self._doPublish(erne, wfTool)
        self.results = log
        return self.render and self.template() or None
            
