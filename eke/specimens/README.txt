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
    >>> browser.getControl(name='specimenCount').value = u'128'
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
    128


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
    >>> browser.getControl(name='protocol:list').displayValue = ['Public Safety']
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
    >>> f.protocol.title
    'Public Safety'


TODO: Addable content to sets: files, pages, images.


Views
-----

Here we'll show how the content types present themselves in a browser.


Specimen Collection Folder
~~~~~~~~~~~~~~~~~~~~~~~~~~

Specimen Collection Folders simply show each of the Specimen Collections they
contain::

    >>> browser.open(portalURL + '/sticky-specimens')
    >>> browser.contents
    '...The Probed Collection...128...'

As you can see, they also show the specimen count.

TODO: Finally, there's a nifty bar chart: >>> browser.contents '...http://chart.apis.google.com...'


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
    '...ANAL-REF...DNA...127...90...45...Public Safety...'

That's all there is.


RDF Ingest
----------

Not supported.  Woot!


.. References:
.. _EKE: http://cancer.jpl.nasa.gov/documents/applications/knowledge-environment
.. _RDF: http://w3.org/RDF/
.. _URI: http://w3.org/Addressing/
