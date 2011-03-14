# encoding: utf-8
# Copyright 2010 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''EDRN Knowledge Environment Specimens: test the setup of this package.
'''

from base import BaseTestCase
from Products.CMFCore.utils import getToolByName
from zope.component import queryUtility
from zope.schema.interfaces import IVocabularyFactory
from eke.specimens import SPECIMEN_TYPE_VOCAB_NAME, STORAGE_VOCAB_NAME
import unittest

class TestSetup(BaseTestCase):
    '''Unit tests the setup of this package.'''
    def testTypes(self):
        '''Make sure our types are available.'''
        types = getToolByName(self.portal, 'portal_types').objectIds()
        for i in (
            'Specimen Folder', 'Specimens at Site in Protocol', 'Specimens in Protocol', 'Specimen Record'
        ):
            self.failUnless(i in types)
    def testTypesNotSearched(self):
        '''Ensure our "structural" types aren't searched by default.'''
        notSearched = self.portal.portal_properties.site_properties.getProperty('types_not_searched')
        for i in ('Specimens in Protocol', 'Specimens at Site in Protocol'): # TODO: Both?
            self.failUnless(i in notSearched)
    def testCatalogIndexes(self):
        '''Check if indexes are properly installed.'''
        catalog = getToolByName(self.portal, 'portal_catalog')
        indexes = catalog.indexes()
        for i in ('specimenCount', 'participantCount', 'identifier', 'specimenType', 'storageType', 'cancerDiagnosis', 'siteName'):
            self.failUnless(i in indexes)
    def testCatalogMetadata(self):
        '''Check if indexed metadata schema are properly installed.'''
        catalog = getToolByName(self.portal, 'portal_catalog')
        metadata = catalog.schema()
        for i in ('specimenCount', 'participantCount', 'identifier'):
            self.failUnless(i in metadata)
    def testVocabularies(self):
        '''Ensure our vocabularies are available'''
        vocabs = (
            SPECIMEN_TYPE_VOCAB_NAME, STORAGE_VOCAB_NAME, u'eke.specimens.CancerDiagnosisVocabulary', u'eke.specimens.ERNESites'
        )
        for v in vocabs:
            self.failUnless(queryUtility(IVocabularyFactory, name=v) is not None)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSetup))
    return suite
    
