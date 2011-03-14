# encoding: utf-8
# Copyright 2010 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''EDRN Knowledge Environment Specimens: test the ingest of specimen data.
'''

from base import BaseTestCase
from eke.specimens.browser.utils import getSpecimens, SpecimenStatistics
import unittest

class SpecimenStatisticsTest(BaseTestCase):
    '''Tests of the SpecimenStatistics class'''
    def testComparisons(self):
        a0 = SpecimenStatistics(True, '3', '5', 10, 10)
        a1 = SpecimenStatistics(True, '3', '5', 10, 10)
        b  = SpecimenStatistics(True, '3', '5', 10,  5)
        c  = SpecimenStatistics(True, '3', '5', 15, 10)
        d = SpecimenStatistics(False, '3', '5', 10, 10)
        e = SpecimenStatistics(True,  '3', '6', 10, 10)
        f = SpecimenStatistics(True,  '4', '5', 10, 10)
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
        a0 = SpecimenStatistics(True, '3', '5', 10, 10)
        a1 = SpecimenStatistics(True, '3', '5', 10, 10)
        b  = SpecimenStatistics(True, '3', '5', 10, 5)
        self.assertEquals(hash(a0), hash(a1))
        self.failUnless(hash(a0) != hash(b))

class TestIngest(BaseTestCase):
    '''Unit tests of ingestion.'''
    def testBadURL(self):
        '''Ensure ``getSpecimens`` raises an exception on bad URLs'''
        self.failUnlessRaises(IOError, getSpecimens, 'bogus:url:to-no-where')
    def testNormalSpecimens(self):
        '''Check if ``getSpecimens`` returns reasonable results on test data'''
        records = getSpecimens('testscheme://localhost/erne/prod', 'testscheme://localhost/erne/erneQuery')
        records.sort()
        self.assertEquals(3, len(records))
        self.assertEquals(SpecimenStatistics(False, '3', ' 1', 2, 2), records[0])
        self.assertEquals(SpecimenStatistics(True, '18', '17', 1, 1), records[1])
        self.assertEquals(SpecimenStatistics(True,  '3',  '3', 2, 1), records[2])

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SpecimenStatisticsTest))
    suite.addTest(unittest.makeSuite(TestIngest))
    return suite
    
