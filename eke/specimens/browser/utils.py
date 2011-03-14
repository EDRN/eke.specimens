# encoding: utf-8
# Copyright 2010 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

from eke.site.interfaces import ISite
from Products.CMFCore.utils import getToolByName
from zope.interface import directlyProvides
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary
import urllib, urllib2, logging

_logger = logging.getLogger(__name__)

_erneWS = 'http://ginger.fhcrc.org/edrn/erneQuery'

_units = {
    '1':  u'mcl',
    '2':  u'ml',
    '3':  u'mcg',
    '4':  u'mg',
    '8':  u'slides',
    '14': u'cells',
    '98': u'',
    '99': u'',
}

_genders = {
    '1': u'Male',
    '2': u'Female',
    '9': u'Refused',
}

_races = {
    '1':	u'White',
    '2':	u'Black/African-American',
    '3':	u'American Indian/Alaska Native',
    '4':	u'Asian',
    '7':	u'Native Hawaiian/Pacific Islander',
    '97':	u'Unspecified',
    '99':	u'Refused/Unknown',
}

_ethnicities = {
    '0':    u'N/A',
    '1':    u'Hispanic/latino',
    '9':    u'Unknown',
}

# Site identifier to ERNE identifier
SITES = {
    'http://edrn.nci.nih.gov/data/sites/73':  'https://supergrover.uchsc.edu:7576/erne/prod',    # Colorado
    'http://edrn.nci.nih.gov/data/sites/203': 'https://profiler.med.cornell.edu:7576/erne/prod', # Beth Israel
    'http://edrn.nci.nih.gov/data/sites/70':  'https://edrn.partners.org:7576/erne/prod',        # Brigham & Women's
    'http://edrn.nci.nih.gov/data/sites/91':  'https://cdc-erne.cdc.gov:7576/erne/prod',         # CDC
    'http://edrn.nci.nih.gov/data/sites/80':  'https://edrn.creighton.edu:7576/erne/prod',       # Creighton Univ
    'http://edrn.nci.nih.gov/data/sites/67':  'https://kepler.dartmouth.edu:7576/erne/prod',     # GLNE Dartmouth
    'http://edrn.nci.nih.gov/data/sites/81':  'https://surg-oodt.mc.duke.edu:7576/erne/prod',    # Duke Univ
    'http://edrn.nci.nih.gov/data/sites/202': 'https://erne.fccc.edu:7576/erne/prod',            # Fox Chase
    'http://edrn.nci.nih.gov/data/sites/83':  'https://162.129.227.245:7576/erne/prod',          # Johns Hopkins Urology
    'http://edrn.nci.nih.gov/data/sites/176': 'https://edrn.med.nyu.edu:7576/grid/prod',         # NYU
    'http://edrn.nci.nih.gov/data/sites/167': 'https://telepath-d340.upmc.edu:7576/erne/prod',   # Pittsburgh
    'http://edrn.nci.nih.gov/data/sites/189': 'https://ucsf-97-101.ucsf.edu:7576/erne/prod',     # UCSF
    'http://edrn.nci.nih.gov/data/sites/408': 'https://erne.ucsd.edu:7576/erne/prod',            # UCSD
}

class SpecimenStatistics(object):
    def __init__(self, withCancer, kind, storage, numSpecs, numPpts):
        self.withCancer, self.numSpecs, self.numPpts = withCancer, numSpecs, numPpts
        self.kind, self.storage = kind.strip(), storage.strip()
    def __repr__(self):
        return '%s(withCancer=%r,kind=%r,storage=%r,numSpecs=%r,numPpts=%r)' % (
            self.__class__.__name__, self.withCancer, self.kind, self.storage, self.numSpecs, self.numPpts
        )
    def __cmp__(self, other):
        rc = cmp(self.withCancer, other.withCancer)
        if rc < 0:
            return -1
        elif rc == 0:
            rc = cmp(self.kind, other.kind)
            if rc < 0:
                return -1
            elif rc == 0:
                rc = cmp(self.storage, other.storage)
                if rc < 0:
                    return -1
                elif rc == 0:
                    rc = cmp(self.numSpecs, other.numSpecs)
                    if rc < 0:
                        return -1
                    elif rc == 0:
                        return cmp(self.numPpts, other.numPpts)
        return 1
    def __hash__(self):
        return self.withCancer << 30 ^ hash(self.kind) << 15 ^ hash(self.storage) << 7 ^ self.numSpecs << 3 ^ self.numPpts

class SpecimenInventory(object):
    def __init__(self, contact, specimens, count, limit):
        self.contact, self.specimens, self.count, self.limit = contact, specimens, count, limit
        # Show specimen collected, storage, cancer diagnosis
        # Then break down # samples # participants by gender, race, smoking history
    def __repr__(self):
        return '%s(contact=%s,# specimens=%d)' % (self.__class__.__name__, self.contact, len(self.specimens))
    def __iter__(self):
        return iter(self.specimens)

class Quantity(object):
    def __init__(self, value, units):
        self.value, self.units = value, units
    def __unicode__(self):
        if self.value in ('unknown', '9999.0', 'blank'): return u'–'
        return u'%s %s' % (self.value, _units.get(self.units, u''))
    
class Specimen(object):
    def __init__(self, pptID, gender, race, ethnicity, icd9, ageAtCollection, ageAtDX, isAvailable, final, collected, remaining):
        self.pptID, self._gender, self._race, self._ethnicity = pptID, gender, race, ethnicity
        self.icd9, self._ageAtCollection, self._ageAtDX, self.isAvailable = icd9, ageAtCollection, ageAtDX, isAvailable
        self.final, self.collected, self.remaining = final, collected, remaining
    @property
    def gender(self):
        return _genders.get(self._gender, u'Unknown') # FIXME: Not i18n
    @property
    def race(self):
        return _races.get(self._race, u'Unknown') # FIXME: Not i18n
    @property
    def ethnicity(self):
        return _ethnicities.get(self._ethnicity, u'Unknown') # FIXME: Not i18n
    @property
    def ageAtCollection(self):
        return self._ageAtCollection in ('999', 'unknown', 'blank') and u'–' or self._ageAtCollection
    @property
    def ageAtDX(self):
        return self._ageAtDX in ('999' or 'unknown') and u'–' or self._ageAtDX
    def __repr__(self):
        return '%s(pptID=%s,gender=%s,race=%s,ethnicity=%s,...)' % (
            self.__class__.__name__, self.pptID, self.gender, self.race, self.ethnicity
        )

def getSpecimens(erneID, erneWS=_erneWS):
    cdes = ('BASELINE_CANCER-CONFIRMATION_CODE', 'SPECIMEN_COLLECTED_CODE', 'SPECIMEN_STORED_CODE', 'STUDY_PARTICIPANT_ID')
    queryStr = ' AND '.join(['RETURN = %s' % cde for cde in cdes])
    params = {'q': queryStr, 'url': erneID}
    con = None
    records = []
    try:
        con = urllib2.urlopen(erneWS, urllib.urlencode(params))
        stats = {}
        for erneRecord in con.read().split('$'):
            fields = erneRecord.split('\t')
            if len(fields) != 4:
                continue
            for i in xrange(0, 4):
                fields[i] = fields[i].strip()
            cancerDiag, spec, storage, ppt = fields
            if not cancerDiag or cancerDiag in ('9', 'unknown', 'blank') or not spec or spec in ('unknown', 'blank') or \
                not storage or storage in ('unknown', 'blank') or not ppt or ppt in ('unknown', 'blank'):
                continue
            diagnoses = stats.get(cancerDiag, {})
            specimenTypes = diagnoses.get(spec, {})
            storageTypes = specimenTypes.get(storage, {})
            specimenCount = storageTypes.get(ppt, 0)
            specimenCount += 1
            storageTypes[ppt] = specimenCount
            specimenTypes[storage] = storageTypes
            diagnoses[spec] = specimenTypes
            stats[cancerDiag] = diagnoses
        for cancerDiag, specimenTypes in stats.iteritems():
            withCancer = cancerDiag == '1' and True or False
            for specType, storageTypes in specimenTypes.iteritems():
                for storageType, pptIDs in storageTypes.iteritems():
                    totalSpecimens = sum(pptIDs.values())
                    totalParticipants = len(pptIDs)
                    records.append(SpecimenStatistics(withCancer, specType, storageType, totalSpecimens, totalParticipants))
        return records
    except urllib2.HTTPError, ex:
        _logger.info('Ignoring failed attempt to get specimens from %s via %s: %r', erneID, erneWS, ex)
    try:
        con.close()
    except (IOError, AttributeError):
        pass
    return records

def getInventory(erneID, withCancer, collection, storage, limit=100, erneWS=_erneWS):
    cdes = (
    	'BASELINE_CANCER-AGE-DIAGNOSIS_VALUE',
    	'BASELINE_CANCER-ICD9-CODE',
    	'BASELINE_DEMOGRAPHICS-ETHNIC_CODE',
    	'BASELINE_DEMOGRAPHICS-GENDER_CODE',
    	'BASELINE_DEMOGRAPHICS_RACE_CODE',
    	'BASELINE_SMOKE-REGULAR_1YEAR_CODE',
    	'SPECIMEN_AGE-COLLECTED_VALUE',
    	'SPECIMEN_AMOUNT-STORED_UNIT_CODE',
    	'SPECIMEN_AMOUNT-STORED_VALUE',
    	'SPECIMEN_AMOUNT_REMAINING_UNIT_CODE',
    	'SPECIMEN_AMOUNT_REMAINING_VALUE',
    	'SPECIMEN_AVAILABLE_CODE',
    	'SPECIMEN_CONTACT-EMAIL_TEXT',
    	'SPECIMEN_FINAL-STORE_CODE',
    	'SPECIMEN_TISSUE_ORGAN-SITE_CODE',
    	'STUDY_PARTICIPANT_ID',
    )
    queryStr = 'BASELINE_CANCER-CONFIRMATION_CODE = %(withCancer)d AND ' + \
        'SPECIMEN_COLLECTED_CODE = %(collection)s AND ' + \
        'SPECIMEN_STORED_CODE = %(storage)s AND %(selection)s'
    queryStr = queryStr % {
        'withCancer': withCancer and 1 or 0,
        'collection': collection,
        'storage':    storage,
        'selection':  ' AND '.join(['RETURN = %s' % cde for cde in cdes])
    }
    params = {'q': queryStr, 'url': erneID}
    con = None
    try:
        con = urllib2.urlopen(erneWS, urllib.urlencode(params))
        contactEmailAddr, specimens = None, []
        count = 0
        for erneRecord in con.read().split('$'):
            fields = erneRecord.split('\t')
            if len(fields) != 16: continue
            count += 1
            if count < limit:
                ageAtDX,icd9,ethnicity,gender,race,smoke,ageAtCol,su,sv,ru,rv,isAvailable,email,final,organ,ppt = fields
                if not contactEmailAddr: contactEmailAddr = email
                collected, remaining = Quantity(sv, su), Quantity(rv, ru)
                s = Specimen(ppt, gender, race, ethnicity, icd9, ageAtCol, ageAtDX, isAvailable, final, collected, remaining)
                specimens.append(s)
        return SpecimenInventory(contactEmailAddr, specimens, count, limit)
    finally:
        try:
            con.close()
        except (IOError, AttributeError):
            pass

def ERNESitesVocabulary(context):
    catalog = getToolByName(context, 'portal_catalog')
    # TODO: filter by review_state?
    results = catalog(object_provides=ISite.__identifier__, identifier=SITES.keys())
    siteNames = frozenset([(i.Title, i.Title) for i in results])
    siteNames = list(siteNames)
    siteNames.sort()
    return SimpleVocabulary.fromItems(siteNames)
directlyProvides(ERNESitesVocabulary, IVocabularyFactory)


if __name__ == '__main__':
    import sys
    # for i in getSpecimens(sys.argv[1]):
    #     print i
    details = getInventory(sys.argv[1], bool(sys.argv[2]), sys.argv[3], sys.argv[4])
    print details
    for i in details:
        print i
     
    
