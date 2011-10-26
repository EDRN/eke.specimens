# encoding: utf-8
# Copyright 2011 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

from interfaces import ISpecimenCollectionFolder
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

def addSampleSpecimenSets(setupTool):
    '''Add sample specimen sets'''
    portal = getToolByName(setupTool, 'portal_url').getPortalObject()
    if 'specimens' in portal.keys():
        portal.manage_delObjects('specimens')
    specimens = portal[portal.invokeFactory('Specimen Collection Folder', 'specimens')]
    specimens.setTitle(u'Specimens')
    specimens.setDescription(u'Specimens collected by EDRN and shared with EDRN.')
    specimens.setText(u'<p>This folder contains specimens available to EDRN and collected in EDRN protocols.</p>')
    
    # Create a collection for PRoBE
    probe = specimens[specimens.invokeFactory('Specimen Collection', 'probe')]
    probe.setTitle(u'PRoBE')
    probe.setDescription(u'PRoBE sets.')
    probe.setText(u'<p>We are not sure what <em>PRoBE</em> means yet.</p>')
    probe.specimenCount = 56342
    
    # Add a PRoBE set
    probeSet = probe[probe.invokeFactory('Specimen Set', 'probe-set')]
    probeSet.setTitle('Anally PRoBEd Set')
    probeSet.setDescription(u'Specimens acquired through anal PRoBing.')
    probeSet.shortName = 'PRoBE-ANUS'
    probeSet.storageType = '17'
    probeSet.specimenCount = 51234
    probeSet.numberCases = 503
    probeSet.numberControls = 6969
    
    # Create a collection for reference sets
    referenceSets = specimens[specimens.invokeFactory('Specimen Collection', 'reference-sets')]
    referenceSets.setTitle(u'Reference Sets')
    referenceSets.setDescription(u'Standard specimen reference sets that serve as sets of standard reference specimens.')
    referenceSets.setText(u'<p>EDRN has access to the specimen <em>reference</em> sets listed below.</p>')
    referenceSets.specimenCount = 4132
    
    # Add three reference sets
    colon = referenceSets[referenceSets.invokeFactory('Specimen Set', 'colon-reference-set')]
    colon.setTitle(u'Colon Reference Set')
    colon.setDescription(COLON_SET_DESCRIPTION)
    colon.shortName = 'GLNE'
    colon.storageType = '1'
    colon.specimenCount = 1234
    colon.numberCases = 50
    colon.numberControls = 69
    lungA = referenceSets[referenceSets.invokeFactory('Specimen Set', 'lung-reference-set-a')]
    lungA.setTitle(u'Lung Reference Set A')
    lungA.setDescription(LUNG_SET_A_DESCRIPTION)
    lungA.shortName = 'LungSetA'
    lungA.storageType = '16'
    lungA.specimenCount = 512
    lungA.numberCases = 356
    lungA.numberControls = 156
    lungB = referenceSets[referenceSets.invokeFactory('Specimen Set', 'lung-reference-set-b')]
    lungB.setTitle(u'Lung Reference Set B')
    lungB.setDescription(LUNG_SET_B_DESCRIPTION)
    lungB.shortName = 'LungSetB'
    lungB.storageType = '15'
    lungB.specimenCount = 233
    lungB.numberCases = 86
    lungB.numberControls = 147
    _doPublish(specimens, getToolByName(portal, 'portal_workflow'))


def addFacetedSearch(setupTool):
    portal = getToolByName(setupTool, 'portal_url').getPortalObject()
    request = portal.REQUEST
    catalog = getToolByName(setupTool, 'portal_catalog')
    results = [i.getObject() for i in catalog(object_provides=ISpecimenCollectionFolder.__identifier__)]
    if len(results) == 0:
        # wtf? catalog must be out of date, because the EDRN portal typically includes
        # one Specimen Collection, created above in ``addSampleSpecimenSets`` in fact!
        if 'specimens' in portal.keys():
            results = [portal['specimens']]
    for specimenCollection in results:
        setFacetedNavigation(specimenCollection, request)
