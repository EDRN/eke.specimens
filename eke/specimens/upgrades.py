# encoding: utf-8
# Copyright 2011–2012 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

from interfaces import ISpecimenSystemFolder
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from utils import setFacetedNavigation

COLON_SET_DESCRIPTION = u'''The Early Detection Research Network and the Great Lakes-New England Clinical, Epidemiological and Validation Center (GLNE CEVC) announces the availability of serum, plasma and urine samples for the early detection for colon cancer.'''
LUNG_SET_A_DESCRIPTION = u'''Reference set A focuses on pre-validation of biomarkers of diagnosis of lung cancer and target lung cancer diagnosed for individuals at high risk for lung cancer or abnormal chest x-ray (CXR) or chest computer tomography (CT) but outside of the context of a CT screening trial. The clinical question to be tested after pre-validation relates to whether a serum/plasma biomarker has added value to current clinical tests (CT scan and/or PET scan) for the diagnostic evaluation of pulmonary nodules and to whether such a biomarker could reduce the number, and the attendant cost, of unnecessary invasive tests (PET or tissue biopsy) or futile thoracotomies.'''
LUNG_SET_B_DESCRIPTION = u'''Reference set B focus on pre-validation of biomarkers of early diagnosis (screening) of lung cancer and targeting a specific population of lung cancer patients diagnosed in the context of a computed tomography (CT)-based screening trial of high risk individuals. The clinical question to be tested after pre-validation relates to whether a serum/plasma biomarker has added diagnostic value to current tests (CT scan and/or PET scan) for the diagnostic evaluation of CT-detected pulmonary nodules.'''

def _doPublish(item, wfTool):
    '''Publish item and all its progeny using the given workflow tool.'''
    try:
        wfTool.doActionFor(item, action='publish')
        item.reindexObject()
    except WorkflowException:
        pass
    for i in item.objectIds():
        subItem = item[i]
        _doPublish(subItem, wfTool)

def nullUpgradeStep(setupTool):
    '''A null step for when a profile upgrade requires no custom activity.'''

def _getProtocolUID(portal, identifier):
    catalog = getToolByName(portal, 'portal_catalog')
    results = catalog(identifier=identifier)
    return results[0].UID if len(results) > 0 else None


def addSampleSpecimenSets(setupTool):
    '''Add sample specimen sets'''
    portal = getToolByName(setupTool, 'portal_url').getPortalObject()
    if 'specimens' in portal.keys():
        portal.manage_delObjects('specimens')
    specimens = portal[portal.invokeFactory('Specimen System Folder', 'specimens')]
    specimens.setTitle(u'Specimens')
    specimens.setDescription(u'Specimens collected by EDRN and shared with EDRN.')
    specimens.setText(u'<p>This folder contains specimens available to EDRN and collected in EDRN protocols.</p>')
    
    # Create a place for ERNE
    erne = specimens[specimens.invokeFactory('ERNE Specimen System', 'erne')]
    erne.setTitle(u'EDRN Specimen System')
    erne.setDescription(u'Early Detection Research Network (EDRN) Resource Network Exchange (ERNE) specimens.')
    erne.setText(u'<p>Includes sites running ERNE product servers as well as other EDRN and affiliate specimen collections.</p>')
    erne.reindexObject()

    # Create a collection for PRoBE
    probe = specimens[specimens.invokeFactory('Specimen System', 'probe')]
    probe.setTitle(u'PRoBE')
    probe.setDescription(u'PRoBE sets.')
    probe.setText(u'<p>We are not sure what <em>PRoBE</em> means yet.</p>')
    
    # Find some PRoBE protocol
    probeProtocolUID = _getProtocolUID(portal, u'http://edrn.nci.nih.gov/data/protocols/337')
    # Add a couple of PRoBE sets
    probeSet = probe[probe.invokeFactory('Generic Specimen Set', 'lung-probed-set')]
    probeSet.setTitle('PRoBE-LUNG')
    probeSet.setDescription(u'Specimens acquired through lung PRoBing.')
    probeSet.fullName = 'Standard PRoBE Set for Lung Biomarkers'
    probeSet.cancerLocations = ('Lung',)
    probeSet.collectionType = ('5', '16')
    probeSet.setStorageType(('16',))
    probeSet.setTotalNumSpecimens(51234)
    probeSet.setProtocol(probeProtocolUID)

    probeSet = probe[probe.invokeFactory('Generic Specimen Set', 'orally-probed-set')]
    probeSet.setTitle('PRoBE-ESO')
    probeSet.setDescription(u'Specimens acquired through esophageal PRoBing.')
    probeSet.fullName = 'Standard PRoBE Set for Esophageal Cancer Markers'
    probeSet.cancerLocations = ('Esophagus', 'Tongue')
    probeSet.collectionType = ('14', '17')
    probeSet.setStorageType(('8', '16'))
    probeSet.setTotalNumSpecimens(49132)
    probeSet.setProtocol(probeProtocolUID)
    probeSet.reindexObject()

    # Create a collection for reference sets
    referenceSets = specimens[specimens.invokeFactory('Specimen System', 'reference-sets')]
    referenceSets.setTitle(u'Reference Sets')
    referenceSets.setDescription(u'Standard specimen reference sets that serve as sets of standard reference specimens.')
    referenceSets.setText(u'<p>EDRN has access to the specimen <em>reference</em> sets listed below.</p>')

    # Add three reference sets
    colon = referenceSets[referenceSets.invokeFactory('Generic Specimen Set', 'colon-reference-set')]
    colon.setTitle('COLON CANCER REF')
    colon.setDescription(u'Standard EDRN reference set for colon cancer.')
    colon.fullName = 'Standard Specimen Reference Set: Colon'
    colon.cancerLocations = ('Colon',)
    colon.collectionType = ('3', '20')
    colon.setStorageType(('2', '3', '18'))
    colon.setTotalNumSpecimens(1234)
    colon.setProtocol(_getProtocolUID(portal, u'http://edrn.nci.nih.gov/data/protocols/251'))
    colon.invokeFactory('Case Control Subset', 'cases', title=u'Cases', subsetType='Case', numParticipants=50)
    colon.invokeFactory('Case Control Subset', 'normals', title=u'Normals', subsetType='Control', numParticipants=50)
    colon.invokeFactory('Case Control Subset', 'ademomas', title=u'Ademomas', subsetType='Control', numParticipants=50)
    colon.reindexObject()

    # colon.setTitle(u'Colon Reference Set')
    # colon.setDescription(COLON_SET_DESCRIPTION)
    # colon.shortName = 'GLNE'
    # colon.organs = ('Colon',)
    # colon.storageType = '1'
    # colon.specimenCount = 1234
    # colon.numberCases = 50
    # colon.numberControls = 69
    # colon.diagnosis = 'With Cancer'
    # lungA = referenceSets[referenceSets.invokeFactory('Specimen Set', 'lung-reference-set-a')]
    # lungA.setTitle(u'Lung Reference Set A')
    # lungA.setDescription(LUNG_SET_A_DESCRIPTION)
    # lungA.shortName = 'LungSetA'
    # lungA.organs = ('Lung',)
    # lungA.storageType = '16'
    # lungA.specimenCount = 512
    # lungA.numberCases = 356
    # lungA.numberControls = 156
    # lungA.diagnosis = 'With Cancer'
    # lungB = referenceSets[referenceSets.invokeFactory('Specimen Set', 'lung-reference-set-b')]
    # lungB.setTitle(u'Lung Reference Set B')
    # lungB.setDescription(LUNG_SET_B_DESCRIPTION)
    # lungB.shortName = 'LungSetB'
    # lungB.organs = ('Lung',)
    # lungB.storageType = '15'
    # lungB.specimenCount = 233
    # lungB.numberCases = 86
    # lungB.numberControls = 147
    # lungB.diagnosis = 'Without Cancer'
    _doPublish(specimens, getToolByName(portal, 'portal_workflow'))
    addFacetedSearch(setupTool)


def addFacetedSearch(setupTool):
    portal = getToolByName(setupTool, 'portal_url').getPortalObject()
    request = portal.REQUEST
    catalog = getToolByName(setupTool, 'portal_catalog')
    results = [i.getObject() for i in catalog(object_provides=ISpecimenSystemFolder.__identifier__)]
    if len(results) == 0:
        # wtf? catalog must be out of date, because the EDRN portal typically includes
        # one Specimen Collection, created above in ``addSampleSpecimenSets`` in fact!
        if 'specimens' in portal.keys():
            results = [portal['specimens']]
    for specimenCollection in results:
        setFacetedNavigation(specimenCollection, request)


def updateDiagnosisIndex(setupTool):
    '''Drop cancerDiagnosis, use diagnosis.'''
    catalog = getToolByName(setupTool, 'portal_catalog')
    schema, indexes = catalog.schema(), catalog.indexes()
    if 'cancerDiagnosis' in schema:
        catalog.delColumn('cancerDiagnosis')
    if 'cancerDiagnosis' in indexes:
        catalog.delIndex('cancerDiagnosis')
    if 'diagnosis' not in indexes:
        catalog.addIndex('diagnosis', 'FieldIndex', {'indexed_attrs': 'diagnosis'})

