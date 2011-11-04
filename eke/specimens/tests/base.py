# encoding: utf-8
# Copyright 2008 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''EDRN Knowledge Environment: Testing base code.
'''

from Products.Five import fiveconfigure
from Products.Five import zcml
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup
from Testing import ZopeTestCase as ztc
import eke.knowledge.tests.base as ekeKnowledgeBase
import eke.site.tests.base as ekeSiteBase
import eke.study.tests.base as ekeStudyBase

# Traditional Products we have to load manually for test cases:
# (none at this time)

@onsetup
def setupEKESite():
    '''Set up additional products required.'''
    fiveconfigure.debug_mode = True
    import eke.specimens
    zcml.load_config('configure.zcml', eke.specimens)
    fiveconfigure.debug_mode = False
    ztc.installPackage('eke.knowledge')
    ztc.installPackage('eke.site')
    ztc.installPackage('eke.study')
    ztc.installPackage('eke.specimens')


setupEKESite()
ptc.setupPloneSite(products=['eke.specimens'])

_siteProtocolRDF = '''<?xml version='1.0' encoding='UTF-8'?>
<rdf:RDF
    xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#'
    xmlns:edrn='http://edrn.nci.nih.gov/rdf/schema.rdf#'>
	<edrn:Site rdf:about='http://tongue.com/clinic/3d'>
        <edrn:hasSpecimensForProtocols>
		    <edrn:Protocol rdf:about='http://swa.it/edrn/ps' specimenCount='123'/>
		    <edrn:Protocol rdf:about='http://swa.it/edrn/so' specimenCount='456'/>
		</edrn:hasSpecimensForProtocols>
	</edrn:Site>
	<edrn:Site rdf:about='http://plain.com/2d'>
		<edrn:hasSpecimensForProtocols>
			<edrn:Protocol rdf:about='http://swa.it/edrn/ps' specimenCount='789'/>
		</edrn:hasSpecimensForProtocols>
	</edrn:Site>
</rdf:RDF>'''

_protocolSpecimensRDF = ''''''

_erneResponse = '''0\t5\t1\tx@y.com\t1$1\t5\t2\tx@y.com\t1$1\t6\t3\tz@y.com\t1$'''

def registerLocalTestData():
    ekeSiteBase.registerLocalTestData()
    ekeStudyBase.registerLocalTestData()
    ekeKnowledgeBase.registerTestData('/erne/a/siteProto', _siteProtocolRDF)
    ekeKnowledgeBase.registerTestData('/erne/a/protoSpec', _protocolSpecimensRDF)
    ekeKnowledgeBase.registerTestData('/erne/erneQuery', _erneResponse)

class BaseTestCase(ekeKnowledgeBase.BaseTestCase):
    '''Base for tests in this package.'''
    def setUp(self):
        super(BaseTestCase, self).setUp()
        registerLocalTestData()
    

class FunctionalBaseTestCase(ekeKnowledgeBase.FunctionalBaseTestCase):
    '''Base class for functional (doc-)tests.'''
    def setUp(self):
        super(FunctionalBaseTestCase, self).setUp()
        registerLocalTestData()
    

