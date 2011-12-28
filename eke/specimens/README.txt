This package provides Plone 3 content objects for the EDRN Knowledge
Environment (EKE_)'s management and display of specimen data.


Content Types
=============

The content types introduced in this package form a narrowing aggregation:

Specimen Folder
    A folder that contains specimen information.  It contains objects of the
    next type.
Specimens at Site in Protocol
    The existence of specimens at a particular EDRN or partner site.  It links
    an EDRN site to specimen collection.  It contains objects of the next
    type.
Specimens in Protocol
    The protocol that guided specimen collection.  It links an EDRN or other
    protocol to specimen collection.  It contains objects of the next type.
Specimen Record
    The record of specimen collection of a single kind.  This records the
    number of specimens collected, the number of participants who gave up
    those specimens, what kind of specimen they were (blood, mucus, feces,
    etc.), how they were stored (in frozen tissue blocks, in zip-top baggies,
    etc.), and whether all of the participants had cancer or none of them did.

The remainder of this document demonstrates the content types using a series
of functional tests.


Tests
=====

In order to execute these tests, we'll first need a test browser::

    >>> from Products.Five.testbrowser import Browser
    >>> browser = Browser()
    >>> portalURL = self.portal.absolute_url()
        
We also change some settings so that any errors will be reported immediately::

    >>> browser.handleErrors = False
    >>> self.portal.error_log._ignored_exceptions = ()
        
We'll also turn off the portlets.  Why?  Well for these tests we'll be looking
for specific strings output in the HTML, and the portlets will often have
duplicate links that could interfere with that::

    >>> from zope.component import getUtility, getMultiAdapter
    >>> from plone.portlets.interfaces import IPortletManager, IPortletAssignmentMapping
    >>> for colName in ('left', 'right'):
    ...     col = getUtility(IPortletManager, name=u'plone.%scolumn' % colName)
    ...     assignable = getMultiAdapter((self.portal, col), IPortletAssignmentMapping)
    ...     for name in assignable.keys():
    ...             del assignable[name]

And finally we'll log in as an administrator::

    >>> from Products.PloneTestCase.setup import portal_owner, default_password
    >>> browser.open(portalURL + '/login_form?came_from=' + portalURL)
    >>> browser.getControl(name='__ac_name').value = portal_owner
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()


Addable Content
---------------

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


Specimen Collection Folder
~~~~~~~~~~~~~~~~~~~~~~~~~~

A Specimen Collection Folder is the top-level container for Specimen
Collections.  They can be added anywhere in the portal::

    >>> browser.open(portalURL)
    >>> l = browser.getLink(id='specimen-collection-folder')
    >>> l.url.endswith('createObject?type_name=Specimen+Collection+Folder')
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


Specimen Collection
~~~~~~~~~~~~~~~~~~~

A Specimen Collection is a top-level curated group of Specimen Sets, such as
the ERNE specimen sets or the PRoBE specimen sets.  They can be added solely
to Specimen Collection Folders::

    >>> browser.open(portalURL)
    >>> browser.getLink(id='specimen-collection')
    Traceback (most recent call last):
    ...
    LinkNotFoundError

So, let's open up the Specimen Collection Folder we made above and add one
there::

    >>> browser.open(portalURL + '/sticky-specimens')
    >>> l = browser.getLink(id='specimen-collection')
    >>> l.url.endswith('createObject?type_name=Specimen+Collection')
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
    >>> f.specimenCount
    0

See that?  The ``specimenCount`` field already knew it was zero since it
computes its value based on contained Specimen Set objects (thank you CA-845).
No Specimen Sets means a zero count.

In fact, the specimenCount field doesn't even appear anymore when you create a
Specimen Collection::

    >>> browser.open(portalURL + '/sticky-specimens')
    >>> browser.getLink(id='specimen-collection').click()
    >>> 'specimenCount' in browser.contents
    False

So, let's add a Specimen Set and see what happens, below.


Specimen Set
~~~~~~~~~~~~

A Specimen Set is a single group of specimens with a collection, such as a set
of PRoBE specimens from a single organ such as the anus, or a set of ERNE
specimens from a single site such as the Anal Research Institute.  They may be
added solely to Specimen Collections::

    >>> browser.open(portalURL)
    >>> browser.getLink(id='specimen-set')
    Traceback (most recent call last):
    ...
    LinkNotFoundError

So let's open the Specimen Collection we created above and add it there::

    >>> browser.open(portalURL + '/sticky-specimens/the-probed-collection')
    >>> l = browser.getLink(id='specimen-set')
    >>> l.url.endswith('createObject?type_name=Specimen+Set')
    True
    >>> l.click()
    >>> browser.getControl(name='title').value = u'Anal Reference Set'
    >>> browser.getControl(name='description').value = u'Official reference set from the anus.'
    >>> browser.getControl(name='shortName').value = u'ANAL-REF'
    >>> browser.getControl(name='storageType').displayValue = ['DNA']
    >>> browser.getControl(name='specimenCount').value = u'127'
    >>> browser.getControl(name='numberCases').value = u'90'
    >>> browser.getControl(name='numberControls').value = u'45'
    >>> browser.getControl(name='organs:lines').value = 'Anus\nRectum'
    >>> browser.getControl(name='diagnosis').displayValue = ['With Cancer']
    >>> browser.getControl(name='protocol:list').displayValue = ['Public Safety']
    >>> browser.getControl(name='site:list').displayValue = ["Dr Tongue's 3D Clinic"]
    >>> browser.getControl(name='form.button.save').click()
    >>> 'anal-reference-set' in f.keys()
    True
    >>> f = f['anal-reference-set']
    >>> f.title
    'Anal Reference Set'
    >>> f.description
    'Official reference set from the anus.'
    >>> f.shortName
    'ANAL-REF'
    >>> f.storageType
    '9'
    >>> f.specimenCount
    127
    >>> f.numberCases
    90
    >>> f.numberControls
    45
    >>> f.organs
    ('Anus', 'Rectum')
    >>> f.diagnosis
    'With Cancer'
    >>> f.protocol.title
    'Public Safety'
    >>> f.site.title
    u"Dr Tongue's 3D Clinic"
    >>> f.siteName
    "Dr Tongue's 3D Clinic"
    >>> f.getCollectionName()
    'The Probed Collection'

You'll notice that the collectionName attribute wasn't available on the form;
that's because it's a computed field.  The siteName works similarly.  Note
that if we change the site, the siteName is updated::

    >>> browser.getLink('Edit').click()
    >>> browser.getControl(name='site:list').displayValue = ['A Plain 2D Clinic']
    >>> browser.getControl(name='form.button.save').click()
    >>> f.siteName
    'A Plain 2D Clinic'

And the parent Specimen Collection now has a non-zero count::

    >>> portal['sticky-specimens']['the-probed-collection'].specimenCount
    127
    >>> portal['sticky-specimens']['the-probed-collection'].specimenCount == f.specimenCount
    True

TODO: Addable content to sets: files, pages, images.


Views
-----

Here we'll show how the content types present themselves in a browser.


Specimen Collection Folder
~~~~~~~~~~~~~~~~~~~~~~~~~~

Specimen Collection Folders show their contents with nifty faceted navigation:

    >>> browser.open(portalURL + '/sticky-specimens')
    >>> browser.contents
    '...faceted-results...Anal Reference Set...'

The facets include the collection, diagnosis, storage, and the site::

    >>> browser.contents
    '...Collection...The Probed Collection...Diagnosis...With Cancer...Without Cancer...Storage...DNA...Site...A Plain 2D Clinic...'

And the displayed results show a table with matching specimen sets, their
collections, the number of specimens, organ site, and their storage type::

    >>> browser.contents
    '...Set/Site...Collection...Specimens...Organ(s)...Storage...'
    >>> browser.contents
    '...Anal Reference Set...>The Probed Collection<...>127</td>...Anus, Rectum...<td>DNA</td>...'

There's a no-break space now between the pound-sign and specimens in the table
heading::

    >>> browser.contents
    '...<table...<thead>...<th>#&#x00a0;Specimens</th>...'

Heather also wants the selection boxes to be narrower::

    >>> browser.contents
    '...#left-area...width: 17em;....left-area-js...margin-left: 17em;...'

Note that they're not so narrow as 15em, but as 17em, because Dan wants ERNE
to be known as "EDRN Specimen System".

There has *got* to be a better way of doing those style changes, though.  See
``faceted_specimens_view.pt`` for explanation.


Specimen Collection
~~~~~~~~~~~~~~~~~~~

Specimen Collections merely show each Specimen Set they contain::

    >>> browser.open(portalURL + '/sticky-specimens/the-probed-collection')
    >>> browser.contents
    '...Anal Reference Set...127...'


Specimen Set
~~~~~~~~~~~~

A Specimen Set just shows off its various attributes::

    >>> browser.open(portalURL + '/sticky-specimens/the-probed-collection/anal-reference-set')
    >>> browser.contents
    '...ANAL-REF...DNA...127...90...45...With Cancer...Public Safety...'

Note that if the specimen set's shortName attribute is empty, then the label
for it won't be shown either (since according to CA-823, Christos was confused
by the strange system-generated identifiers).  Let's create a specimen with no
shortName::

    >>> browser.open(portalURL + '/sticky-specimens/the-probed-collection')
    >>> browser.getLink(id='specimen-set').click()
    >>> browser.getControl(name='title').value = u'Some Other Set'
    >>> browser.getControl(name='storageType').displayValue = ['Plasma']
    >>> browser.getControl(name='specimenCount').value = u'128'
    >>> browser.getControl(name='numberCases').value = u'91'
    >>> browser.getControl(name='numberControls').value = u'46'
    >>> browser.getControl(name='organs:lines').value = 'Sphincter'
    >>> browser.getControl(name='diagnosis').displayValue = ['With Cancer']
    >>> browser.getControl(name='form.button.save').click()

Any short name?  Let's see::

    >>> 'Short Name' in browser.contents
    False
    
That's all there is.  (Well there's something about specimen sharing, but
screw that for now.  It's nearly midnight.)


RDF Ingest
----------

Not supported.  Woot!


.. References:
.. _EKE: http://cancer.jpl.nasa.gov/documents/applications/knowledge-environment
.. _RDF: http://w3.org/RDF/
.. _URI: http://w3.org/Addressing/
