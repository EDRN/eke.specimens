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
            'Specimen Collection Folder', 'Specimen Collection'
        ):
            self.failUnless(i in types)
    def testCatalogIndexes(self):
        '''Check if indexes are properly installed.'''
        catalog = getToolByName(self.portal, 'portal_catalog')
        indexes = catalog.indexes()
        for i in ('specimenCount',):
            self.failUnless(i in indexes)
    def testCatalogMetadata(self):
        '''Check if indexed metadata schema are properly installed.'''
        catalog = getToolByName(self.portal, 'portal_catalog')
        metadata = catalog.schema()
        for i in ('specimenCount',):
            self.failUnless(i in metadata)
    def testAddons(self):
        '''Check that dependent packages are installed'''
        qi = getToolByName(self.portal, 'portal_quickinstaller')
        # TODO: When we migrate from Archetypes to Dexterity, check for plone.app.dexterity
        # self.failUnless(qi.isProductInstalled('plone.app.dexterity'), "Dexterity wasn't installed")


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSetup))
    return suite
    
