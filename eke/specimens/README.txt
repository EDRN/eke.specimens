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


ERNE
----

The EDRN Resource Network Exchange or ERNE also tracks specimens, sometimes
with online sites that run OODT Product Servers to do real-time queries,
sometimes with static data loaded into the ERNE cache.  Some sites are former
ERNE sites that have only passing affiliation with EDRN.  The former we
represent with Active ERNE Set objects, the latter with Inactive ERNE Sets.
Both of these may be added solely to ERNE Systems.


ERNE System
~~~~~~~~~~~

An ERNE System is just like the more generic Specimen System, except that it's
for ERNE specimen sets, and it has an ingest method to bring in ERNE data.
ERNE Systems may be added only to Specimen System Folders::

    >>> browser.open(portalURL)
    >>> browser.getLink(id='erne-specimen-system')
    Traceback (most recent call last):
    ...
    LinkNotFoundError

So, let's open up the Specimen System Folder we made above and add one there::

    >>> browser.open(portalURL + '/sticky-specimens')
    >>> l = browser.getLink(id='erne-specimen-system')
    >>> l.url.endswith('createObject?type_name=ERNE+Specimen+System')
    True
    >>> l.click()
    >>> browser.getControl(name='title').value = u'Ernie'
    >>> browser.getControl(name='description').value = u"Ernie's specimens."
    >>> browser.getControl(name='text').value = u'<p>Warning: may solely be comprised of felt or plastic.</p>'
    >>> browser.getControl(name='form.button.save').click()
    >>> 'ernie' in portal['sticky-specimens'].keys()
    True
    >>> f = portal['sticky-specimens']['ernie']
    >>> f.title
    'Ernie'
    >>> f.description
    "Ernie's specimens."
    >>> f.text
    '<p>Warning: may solely be comprised of felt or plastic.</p>'
    >>> f.getTotalNumSpecimens()
    0

As before, the folder starts out with zero specimens since there's nothing
inside of it to contribute to the total.

No problem, though, let's add some specimens…


Inactive ERNE Set
~~~~~~~~~~~~~~~~~

An Inactive ERNE Set is like a General Specimen Set except that it tracks
summary information about a specimens stored at a former EDRN site.  They
can't be added just anywhere::

    >>> browser.open(portalURL)
    >>> browser.getLink(id='inactive-erne-set')
    Traceback (most recent call last):
    ...
    LinkNotFoundError

Nor to the more generic Specimen System container::

    >>> browser.open(portalURL + '/sticky-specimens/the-probed-collection')
    >>> l = browser.getLink(id='inactive-erne-set')
    Traceback (most recent call last):
    ...
    LinkNotFoundError

But we can add it to the ERNE Specimen System we made above::

    >>> browser.open(portalURL + '/sticky-specimens/ernie')
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
    >>> browser.getControl(name='collectionType').displayValue = ['Stool']
    >>> browser.getControl(name='contactName').value = u'Joe Proctologist'
    >>> browser.getControl(name='form.button.save').click()
    >>> e = portal['sticky-specimens']['ernie']['dead-anus-set']
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
    '18'
    >>> e.contactName
    'Joe Proctologist'
    >>> e.getTotalNumSpecimens()
    0
    >>> len(e.getStorageType()) == 0
    True
    >>> e.getSystemName()
    'Ernie'

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
    >>> import transaction; transaction.commit()

And check out the system::

    >>> portal['sticky-specimens']['ernie'].getTotalNumSpecimens()
    33

Viewing one is simplistic::

    >>> browser.open(portalURL + '/sticky-specimens/ernie/dead-anus-set')
    >>> browser.contents
    '...Dead Anus Set...An inactive ERNE site...33...Public Safety...Dr Tongue...rectum, anus...Stool...Joe Proctologist...'

Yep, it's just the attributes.

Now for the fun part…


Active ERNE Set
~~~~~~~~~~~~~~~

Active ERNE Sets aren't normally created by hand; more often they're ingested
from the ERNE system and created via the ingest method.  However, let's make
sure they work by creating one by hand and check all the fields.  First off,
note that like Inactive ERNE Sets, they can't just be added willy-nilly
anywhere::

    >>> browser.open(portalURL)
    >>> browser.getLink(id='active-erne-set')
    Traceback (most recent call last):
    ...
    LinkNotFoundError

They can't go into the generic Specimen System container either::

    >>> browser.open(portalURL + '/sticky-specimens/the-probed-collection')
    >>> l = browser.getLink(id='active-erne-set')
    Traceback (most recent call last):
    ...
    LinkNotFoundError

But we can add it to the ERNE Specimen System we made above::

    >>> browser.open(portalURL + '/sticky-specimens/ernie')
    >>> l = browser.getLink(id='active-erne-set')
    >>> l.url.endswith('createObject?type_name=Active+ERNE+Set')
    True
    >>> l.click()
    >>> browser.getControl(name='title').value = u'Live Anus Set'
    >>> browser.getControl(name='totalNumSpecimens').value = u'109'
    >>> browser.getControl(name='description').value = u'An active ERNE set actively producing anal samples!'
    >>> browser.getControl(name='protocol:list').displayValue = ['Public Safety']
    >>> browser.getControl(name='text').value = u'<p>Producing <em>more</em> samples than Mr Chunks!</p>'
    >>> browser.getControl(name='site:list').displayValue = ["Dr Tongue's 3D Clinic"]
    >>> browser.getControl(name='organs:lines').value = 'anus\ncolon'
    >>> browser.getControl(name='collectionType').displayValue = ['Seminal fluid']
    >>> browser.getControl(name='storageType').displayValue = ['Cells']
    >>> browser.getControl(name='numCases').value = '32'
    >>> browser.getControl(name='numControls').value = '42'
    >>> browser.getControl(name='diagnosis').displayValue = ['With Cancer']
    >>> browser.getControl(name='form.button.save').click()
    >>> e = portal['sticky-specimens']['ernie']['live-anus-set']
    >>> e.title
    'Live Anus Set'
    >>> e.description
    'An active ERNE set actively producing anal samples!'
    >>> e.protocol.title
    'Public Safety'
    >>> e.text
    '<p>Producing <em>more</em> samples than Mr Chunks!</p>'
    >>> e.site.title
    u"Dr Tongue's 3D Clinic"
    >>> e.organs
    ('anus', 'colon')
    >>> e.collectionType
    '15'
    >>> e.getStorageType()
    '14'
    >>> e.numCases
    32
    >>> e.numControls
    42
    >>> e.diagnosis
    'With Cancer'
    >>> e.getTotalNumSpecimens()
    109
    >>> e.getSystemName()
    'Ernie'

Notice the "Ernie" container's specimen count now::

    >>> portal['sticky-specimens']['ernie'].reindexObject()
    >>> portal['sticky-specimens']['ernie'].getTotalNumSpecimens()
    142

The 109 specimens in the active set boosted the count of the container up from
just 32.

What does an Active ERNE Site look like?  See for yourself:

    >>> browser.open(portalURL + '/sticky-specimens/ernie/live-anus-set')
    >>> browser.contents
    '...Live Anus Set...actively producing anal samples...109...Public Safety...Dr Tongue...anus, colon...Seminal fluid...'
    >>> browser.contents
    '...Seminal fluid...Cells...32...42...With Cancer...Mr Chunks!...'

Yes, just another attribute rundown.


.. Searching
.. ---------
.. 
.. The real centerpiece of ERNE is, of course, the nifty faceted display.  That
.. happens automatically when you create a Specimen System Folder.  No, really::
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


RDF Ingest
----------

Not supported.  Woot!


.. References:
.. _EKE: http://cancer.jpl.nasa.gov/documents/applications/knowledge-environment
.. _RDF: http://w3.org/RDF/
.. _URI: http://w3.org/Addressing/
