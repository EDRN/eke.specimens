This package provides Plone 3 content objects for the EDRN Knowledge
Environment (EKE_)'s management and display of specimen data.


Content Types
=============

The content types introduced in this package form a narrowing aggregation:

Specimen System Folder
    A folder that contains specimen information.  It contains objects of the
    next type.


The remainder of this document demonstrates the content types using a series
of functional tests.


Tests
=====

First we have to set up some things and login to the site::

    >>> app = layer['app']
    >>> from plone.testing.z2 import Browser
    >>> from plone.app.testing import SITE_OWNER_NAME, SITE_OWNER_PASSWORD
    >>> browser = Browser(app)
    >>> browser.handleErrors = False
    >>> browser.addHeader('Authorization', 'Basic %s:%s' % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD))
    >>> portal = layer['portal']    
    >>> portalURL = portal.absolute_url()

We'll also have a second browser that's unprivileged for some later
demonstrations::

    >>> unprivilegedBrowser = Browser(app)

Now we can check out the new types introduced in this package.


Testing Setup
-------------

Here we'll exercise some of the content objects available in this project and
demonstrate their properties and constraints.  However, before we do some,
let's get some additional content into the portal which we'll rely on.  First
off, we'll need site data, since sites have specimen collections::

    >>> browser.open(portalURL)
    >>> browser.getLink(id='site-folder').click()
    >>> browser.getControl(name='title').value = 'Questionable Sites'
    >>> browser.getControl(name='description').value = 'This folder is just for functional tests.'
    >>> browser.getControl(name='rdfDataSource').value = 'testscheme://localhost/sites/b'
    >>> browser.getControl(name='peopleDataSource').value = 'testscheme://localhost/people/b'
    >>> browser.getControl(name='form.button.save').click()
    >>> browser.open(portalURL + '/questionable-sites/ingest')

We'll also need protocols, since specimens are collected under the guidance of
a protocol::

    >>> browser.open(portalURL)
    >>> browser.getLink(id='study-folder').click()
    >>> browser.getControl(name='title').value = 'Questionable Studies'
    >>> browser.getControl(name='description').value = 'This folder is just for functional tests.'
    >>> browser.getControl(name='rdfDataSource').value = 'testscheme://localhost/protocols/a'
    >>> browser.getControl(name='form.button.save').click()
    >>> browser.open(portalURL + '/questionable-studies/ingest')

The test data source ``testscheme://localhost/protocols/a`` has just one
protocol record in it, so let's ingest from another data source so we can get
at least one more protocol::

    >>> browser.open(portalURL)
    >>> browser.getLink(id='study-folder').click()
    >>> browser.getControl(name='title').value = 'Additional Studies'
    >>> browser.getControl(name='description').value = 'This folder is just for functional tests.'
    >>> browser.getControl(name='rdfDataSource').value = 'testscheme://localhost/protocols/b'
    >>> browser.getControl(name='form.button.save').click()
    >>> browser.open(portalURL + '/additional-studies/ingest')

Now, let's flex.


Non-ERNE Specimen Systems
-------------------------

A Specimen System Folder is the top-level container for Specimen Systems.
They can be added anywhere in the portal::

    >>> browser.open(portalURL)
    >>> l = browser.getLink(id='specimen-system-folder')
    >>> l.url.endswith('createObject?type_name=Specimen+System+Folder')
    True
    >>> l.click()
    >>> browser.getControl(name='title').value = u'Sticky Specimens'
    >>> browser.getControl(name='description').value = u'This folder is just for functional tests.'
    >>> browser.getControl(name='text').value = u'<p>Warning: these are <em>sticky</em> specimens.</p>'
    >>> browser.getControl(name='form.button.save').click()
    >>> 'sticky-specimens' in portal.keys()
    True
    >>> f = portal['sticky-specimens']
    >>> f.title
    'Sticky Specimens'
    >>> f.description
    'This folder is just for functional tests.'
    >>> f.text
    '<p>Warning: these are <em>sticky</em> specimens.</p>'    

Moving on…


Specimen System
~~~~~~~~~~~~~~~

A Specimen System is a top-level curated group of Specimen Sets, such as
the the PRoBE specimen sets.  They can be added solely to Specimen System
Folders::

    >>> browser.open(portalURL)
    >>> browser.getLink(id='specimen-system')
    Traceback (most recent call last):
    ...
    LinkNotFoundError

So, let's open up the Specimen System Folder we made above and add one there::

    >>> browser.open(portalURL + '/sticky-specimens')
    >>> l = browser.getLink(id='specimen-system')
    >>> l.url.endswith('createObject?type_name=Specimen+System')
    True
    >>> l.click()
    >>> browser.getControl(name='title').value = u'The Probed Collection'
    >>> browser.getControl(name='description').value = u'Collection of specimens obtained through probing.'
    >>> browser.getControl(name='text').value = u'<p>Warning: some specimens from <strong>unwilling</strong> participants.</p>'
    >>> browser.getControl(name='form.button.save').click()
    >>> 'the-probed-collection' in f.keys()
    True
    >>> f = f['the-probed-collection']
    >>> f.title
    'The Probed Collection'
    >>> f.description
    'Collection of specimens obtained through probing.'
    >>> f.text
    '<p>Warning: some specimens from <strong>unwilling</strong> participants.</p>'
    >>> f.getTotalNumSpecimens()
    0

See that?  The ``totalNumSpecimens`` field already knew it was zero since it
computes its value based on contained Specimen Set objects (thank you CA-845).
No Specimen Sets means a zero count.  As such, it's not even an editable
field::

    >>> browser.open(portalURL + '/sticky-specimens')
    >>> browser.getLink(id='specimen-system').click()
    >>> 'totalNumSpecimens' in browser.contents
    False

Let's add a Specimen Set to this system and see what happens, below.


Generic Specimen Set
~~~~~~~~~~~~~~~~~~~~

A Generic Specimen Set is a single group of specimens with a collection, such
as a set of PRoBE specimens from a single organ such as the anus.  They may be
added solely to Specimen Systems::

    >>> browser.open(portalURL)
    >>> browser.getLink(id='generic-specimen-set')
    Traceback (most recent call last):
    ...
    LinkNotFoundError

So let's open the Specimen System we created above and add it there::

    >>> browser.open(portalURL + '/sticky-specimens/the-probed-collection')
    >>> l = browser.getLink(id='generic-specimen-set')
    >>> l.url.endswith('createObject?type_name=Generic+Specimen+Set')
    True
    >>> l.click()
    >>> browser.getControl(name='title').value = u'ANAL-REF'
    >>> browser.getControl(name='description').value = u'Official reference set from the anus.'
    >>> browser.getControl(name='totalNumSpecimens').value = u'127'
    >>> browser.getControl(name='protocol:list').displayValue = ['Public Safety']
    >>> browser.getControl(name='text').value = u'<p>Heaps of specimens from the booty.</p>'
    >>> browser.getControl(name='fullName').value = u'Anal Reference Set'
    >>> browser.getControl(name='collectionType:list').displayValue = ['Ascites', 'Stool']
    >>> browser.getControl(name='cancerLocations:lines').value = 'rectum\nanus\ncolon'
    >>> browser.getControl(name='storageType:list').displayValue = ['DNA', 'RNA']
    >>> browser.getControl(name='form.button.save').click()
    >>> 'anal-ref' in f.keys()
    True
    >>> f = f['anal-ref']
    >>> f.title
    'ANAL-REF'
    >>> f.description
    'Official reference set from the anus.'
    >>> f.getTotalNumSpecimens()
    127
    >>> f.protocol.title
    'Public Safety'
    >>> f.text
    '<p>Heaps of specimens from the booty.</p>'
    >>> f.fullName
    'Anal Reference Set'
    >>> f.cancerLocations
    ('rectum', 'anus', 'colon')
    >>> f.collectionType
    ('1', '18')
    >>> f.getStorageType()
    ('9', '10')
    >>> f.cancerLocations
    ('rectum', 'anus', 'colon')
    >>> f.getSystemName()
    'The Probed Collection'
    >>> f.getNumParticipants()
    0
    >>> f.getNumCases()
    0
    >>> f.getNumControls()
    0

You'll notice that the ``systemName`` attribute wasn't available on the form;
that's because it's a computed field::

    >>> browser.open(portalURL + '/sticky-specimens/the-probed-collection')
    >>> browser.getLink(id='generic-specimen-set').click()
    >>> 'systemName' in browser.contents
    False

As are the numbers of participants, cases, and controls::

    >>> 'numParticipants' in browser.contents
    False
    >>> 'numCases' in browser.contents
    False
    >>> 'numControls' in browser.contents
    False

We'll see more about cases and control in just a moment.  First, let's see if
the Specimen System updated its total::

    >>> portal['sticky-specimens']['the-probed-collection'].getTotalNumSpecimens()
    127
    >>> portal['sticky-specimens']['the-probed-collection'].getTotalNumSpecimens() == f.getTotalNumSpecimens()
    True

Great!  What else can you do with a General Specimen Set?  You can add files
to it::

    >>> from StringIO import StringIO
    >>> fakeFile = StringIO('%PDF-1.5\nThis is sample PDF file in disguise.\nDo not try to render it.')
    >>> browser.open(portalURL + '/sticky-specimens/the-probed-collection/anal-ref')
    >>> l = browser.getLink(id='file')
    >>> l.url.endswith('createObject?type_name=File')
    True
    >>> l.click()
    >>> browser.getControl(name='title').value = u'My New File'
    >>> browser.getControl(name='description').value = u'A file for functional tests.'
    >>> browser.getControl(name='file_file').add_file(fakeFile, 'application/pdf', 'test.pdf')
    >>> browser.getControl(name='form.button.save').click()

And links, too::

    >>> browser.open(portalURL + '/sticky-specimens/the-probed-collection/anal-ref')
    >>> l = browser.getLink(id='link')
    >>> l.url.endswith('createObject?type_name=Link')
    True
    >>> l.click()
    >>> browser.getControl(name='title').value = u'My New Link'
    >>> browser.getControl(name='description').value = u'A link for functional tests.'
    >>> browser.getControl(name='remoteUrl').value = u'http://google.com/'
    >>> browser.getControl(name='form.button.save').click()

And case/control subsets::

    >>> browser.open(portalURL + '/sticky-specimens/the-probed-collection/anal-ref')
    >>> l = browser.getLink(id='case-control-subset')
    >>> l.url.endswith('createObject?type_name=Case+Control+Subset')
    True
    >>> l.click()
    >>> browser.getControl(name='title').value = u'DCIS'
    >>> browser.getControl(name='description').value = u'WTF is DCIS?'
    >>> browser.getControl(name='subsetType').displayValue = ['Case']
    >>> browser.getControl(name='numParticipants').value = u'48'
    >>> browser.getControl(name='form.button.save').click()
    >>> browser.open(portalURL + '/sticky-specimens/the-probed-collection/anal-ref')
    >>> browser.getLink(id='case-control-subset').click()
    >>> browser.getControl(name='title').value = u'LCIS'
    >>> browser.getControl(name='description').value = u'WTF is LCIS?'
    >>> browser.getControl(name='subsetType').displayValue = ['Case']
    >>> browser.getControl(name='numParticipants').value = u'7'
    >>> browser.getControl(name='form.button.save').click()
    >>> browser.open(portalURL + '/sticky-specimens/the-probed-collection/anal-ref')
    >>> browser.getLink(id='case-control-subset').click()
    >>> browser.getControl(name='title').value = u'Normals'
    >>> browser.getControl(name='description').value = u'WTF is normal?'
    >>> browser.getControl(name='subsetType').displayValue = ['Control']
    >>> browser.getControl(name='numParticipants').value = u'276'
    >>> browser.getControl(name='form.button.save').click()
    
Check out what those did to the numbers of participants, cases, and controls::

    >>> f.getNumParticipants()
    331
    >>> f.getNumCases()
    55
    >>> f.getNumControls()
    276

That's right!  The case/control totals are computed from the case/control
subsets added to the General Specimen Set, and they in turn update the total
number of participants.

When you look at a Generic Specimen Set, you should see its various
attributes::

    >>> browser.open(portalURL + '/sticky-specimens/the-probed-collection/anal-ref')
    >>> browser.contents
    '...Anal Reference Set...Official reference set...ANAL-REF...127...331...Public Safety...'
    >>> browser.contents
    '...Public Safety...Cancer Locations...rectum, anus, colon...'
    >>> browser.contents
    '...rectum, anus, colon...Ascites, Stool...DNA, RNA...Heaps of specimens...'

It should also have the case/control groups, followed by the matching
protocol's abstract (if available), or description (if the abstract wasn't
available)::

    >>> browser.contents
    '...Cases...Total...55...DCIS...48...LCIS...7...Controls...Total...276...Normals...276...Abstract...Clinic surveillance...'

Lastly, it should show the attached files and the links::

    >>> browser.contents
    '...Attached Files...href="...my-new-file"...My New File...Links...My New Link...'


Inactive ERNE Set
~~~~~~~~~~~~~~~~~

An Inactive ERNE Set is like a General Specimen Set except that it tracks
summary information about a specimens stored at a former EDRN site.  They can
be added only to Specimen Systems::

    >>> browser.open(portalURL)
    >>> browser.getLink(id='inactive-erne-set')
    Traceback (most recent call last):
    ...
    LinkNotFoundError

So let's open the Specimen System we created above and add it there::

    >>> browser.open(portalURL + '/sticky-specimens/the-probed-collection')
    >>> l = browser.getLink(id='inactive-erne-set')
    >>> l.url.endswith('createObject?type_name=Inactive+ERNE+Set')
    True
    >>> l.click()
    >>> browser.getControl(name='title').value = u'Dead Anus Set'
    >>> browser.getControl(name='description').value = u'An inactive ERNE site that used to do anal sampling.'
    >>> browser.getControl(name='protocol:list').displayValue = ['Public Safety']
    >>> browser.getControl(name='text').value = u'<p>Collected from deceased booties.</p>'
    >>> browser.getControl(name='site:list').displayValue = ["Dr Tongue's 3D Clinic"]
    >>> browser.getControl(name='organs:lines').value = 'rectum\nanus'
    >>> browser.getControl(name='collectionType:list').displayValue = ['Ascites', 'Stool']
    >>> browser.getControl(name='contactName').value = u'Joe Proctologist'
    >>> browser.getControl(name='form.button.save').click()
    >>> e = portal['sticky-specimens']['the-probed-collection']['dead-anus-set']
    >>> e.title
    'Dead Anus Set'
    >>> e.description
    'An inactive ERNE site that used to do anal sampling.'
    >>> e.protocol.title
    'Public Safety'
    >>> e.text
    '<p>Collected from deceased booties.</p>'
    >>> e.site.title
    u"Dr Tongue's 3D Clinic"
    >>> e.organs
    ('rectum', 'anus')
    >>> e.collectionType
    ('1', '18')
    >>> e.contactName
    'Joe Proctologist'
    >>> e.getTotalNumSpecimens()
    0
    >>> len(e.getStorageType()) == 0
    True

Again, zero specimens to start out.  Why?  Because that value's computed from
stored specimens.

The stored specimens use the Products.DataGridField field-and-widget
combination to edit and display that data.  However, because it uses
Javascript to make the widget interactive, we can't test it through the test
browser.

However, we can manually set the field and see if computed values make sense::

    >>> values = [dict(storageType='1', totalNumSpecimens='11'), dict(storageType='2', totalNumSpecimens='22')]
    >>> e.setSpecimensByStorageType(values)
    >>> e.getTotalNumSpecimens()
    33
    >>> e.getStorageType()
    ('1', '2')
    >>> e.reindexObject()

And check out the system::

    >>> portal['sticky-specimens']['the-probed-collection'].getTotalNumSpecimens()
    160

That's right, 33 new specimens bumped the count up from 127 to 160.





.. Views
.. -----
.. 
.. Here we'll show how the content types present themselves in a browser.
.. 
.. 
.. Specimen System Folder
.. ~~~~~~~~~~~~~~~~~~~~~~
.. 
.. Specimen Collection Folders show their contents with nifty faceted navigation:
.. 
..     >>> browser.open(portalURL + '/sticky-specimens')
..     >>> browser.contents
..     '...faceted-results...Anal Reference Set...'
.. 
.. The facets include the specimen system, diagnosis, storage, collection, and
.. the site::
.. 
..     >>> browser.contents
..     '...System...The Probed Collection...Diagnosis...With Cancer...Without Cancer...Storage...DNA...Collection...Ascites...Site...A Plain 2D Clinic...'
.. 
.. And the displayed results show a table with matching specimen sets, their
.. collections, the number of specimens, organ site, and their storage type::
.. 
..     >>> browser.contents
..     '...Set...System...Storage...Collected...Specimens...'
..     >>> browser.contents
..     '...Anal Reference Set...>The Probed Collection<...>Whole blood</td>...Blood...<td>3126</td>...'
.. 
.. There's a no-break space now between the pound-sign and specimens in the table
.. heading::
.. 
..     >>> browser.contents
..     '...<table...<thead>...<th>#&#x00a0;Specimens</th>...'
.. 
.. Heather also wants the selection boxes to be narrower::
.. 
..     >>> browser.contents
..     '...#left-area...width: 17em;....left-area-js...margin-left: 17em;...'
.. 
.. Note that they're not so narrow as 15em, but as 17em, because Dan wants ERNE
.. to be known as "EDRN Specimen System".
.. 
.. There has *got* to be a better way of doing those style changes, though.  See
.. ``faceted_specimens_view.pt`` for explanation.
.. 
.. 
.. Specimen System
.. ~~~~~~~~~~~~~~~
.. 
.. Specimen Systems merely show each specimen set they contain::
.. 
..     >>> browser.open(portalURL + '/sticky-specimens/the-probed-collection')
..     >>> browser.contents
..     '...Anal Reference Set...127...Dead Anus Set...326...'
.. 
.. 
.. Generic Specimen Set
.. ~~~~~~~~~~~~~~~~~~~~
.. 
.. A Generic Specimen Set just shows off its various attributes::
.. 
..     >>> browser.open(portalURL + '/sticky-specimens/the-probed-collection/anal-ref')
..     >>> browser.contents
..     '...ANAL-REF...DNA...RNA...127...90...45...Public Safety...'
.. 
.. Note that if the specimen set's shortName attribute is empty, then the label
.. for it won't be shown either (since according to CA-823, Christos was confused
.. by the strange system-generated identifiers).  Let's create a specimen with no
.. shortName::
.. 
..     >>> browser.open(portalURL + '/sticky-specimens/the-probed-collection')
..     >>> browser.getLink(id='specimen-set').click()
..     >>> browser.getControl(name='title').value = u'Some Other Set'
..     >>> browser.getControl(name='storageType').displayValue = ['Plasma']
..     >>> browser.getControl(name='specimenCount').value = u'128'
..     >>> browser.getControl(name='numberCases').value = u'91'
..     >>> browser.getControl(name='numberControls').value = u'46'
..     >>> browser.getControl(name='organs:lines').value = 'Sphincter'
..     >>> browser.getControl(name='diagnosis').displayValue = ['With Cancer']
..     >>> browser.getControl(name='form.button.save').click()
.. 
.. Any short name?  Let's see::
.. 
..     >>> 'Short Name' in browser.contents
..     False
..     
.. That's all there is.
.. 
.. 
.. ERNE
.. ----
.. 
.. TBD.
.. 
.. 
.. RDF Ingest
.. ----------
.. 
.. Not supported.  Woot!
.. 
.. 
.. .. References:
.. .. _EKE: http://cancer.jpl.nasa.gov/documents/applications/knowledge-environment
.. .. _RDF: http://w3.org/RDF/
.. .. _URI: http://w3.org/Addressing/
