# encoding: utf-8
# Copyright 2010 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''EDRN Knowledge Environment Specimens: test the ingest of specimen data.
'''

from base import BaseTestCase
from eke.specimens.browser.utils import getSpecimens, ERNESpecimenSummary
import unittest

class SpecimenSummaryTest(BaseTestCase):
    '''Tests of the SpecimenSummary class'''
    def testComparisons(self):
        a0 = ERNESpecimenSummary('3', 123, 10, 5, True, True, 'x@y.com')
        a1 = ERNESpecimenSummary('3', 123, 10, 5, True, True, 'x@y.com')
        b  = ERNESpecimenSummary('3', 123, 10, 5, True, True, 'w@y.com')
        c  = ERNESpecimenSummary('3', 123, 10, 5, True, True, 'z@x.com')
        d  = ERNESpecimenSummary('2', 123, 10, 5, True, True, 'x@y.com')
        e  = ERNESpecimenSummary('3', 123, 10, 6, True, True, 'x@y.com')
        f  = ERNESpecimenSummary('3', 124, 10, 5, True, True, 'x@y.com')
        self.assertEquals(a0, a0)
        self.assertEquals(a0, a1)
        self.failUnless(a0 != b)
        self.failUnless(a0 <= a1)
        self.failUnless(a0 >= b)
        self.failUnless(a0 > b)
        self.failUnless(a0 <= c)
        self.failUnless(a0 < c)
        self.failUnless(a0 >= d)
        self.failUnless(a0 > d)
        self.failUnless(d < b < a0)
        self.failUnless(a0 < e)
        self.failUnless(a0 < f)
    def testHashability(self):
        a0 = ERNESpecimenSummary('3', 123, 10, 5, True, True, 'x@y.com')
        a1 = ERNESpecimenSummary('3', 123, 10, 5, True, True, 'x@y.com')
        b  = ERNESpecimenSummary('3', 123, 10, 5, True, True, 'x@z.com')
        self.assertEquals(hash(a0), hash(a1))
        self.failUnless(hash(a0) != hash(b))

class IngestTest(BaseTestCase):
    '''Unit tests of ingestion.'''
    def testBadURL(self):
        '''Ensure ``getSpecimens`` returns no specimens for bad URLs'''
        records = getSpecimens('bogus:url:to-no-where')
        self.assertEquals(0, len(records))
    def testNormalSpecimens(self):
        '''Check if ``getSpecimens`` returns reasonable results on test data'''
        records = getSpecimens('testscheme://localhost/erne/prod', 'testscheme://localhost/erne/erneQuery')
        records.sort()
        self.assertEquals(3, len(records))
        self.assertEquals(ERNESpecimenSummary('5', 1, 1, 0, False, True, 'z@y.com'), records[0])
        self.assertEquals(ERNESpecimenSummary('5', 1, 1, 0, True, True, 'z@y.com'), records[1])
        self.assertEquals(ERNESpecimenSummary('6', 1, 1, 0, True, True, 'z@y.com'), records[2])

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SpecimenSummaryTest))
    suite.addTest(unittest.makeSuite(IngestTest))
    return suite
    
