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


Specimen Folder
~~~~~~~~~~~~~~~

A Specimen Folder doesn't actually contain specimen objects.  There are
thousands upon thousands of specimens, and having a separate object for each
one in the portal is silly, even if doable.  (Instead, let them all live in
their various distributed relational databases spread throughout ERNE.) The
job of a Specimen Folder is to contain summary information about specimens.

They can be added anywhere in the portal::

    >>> browser.open(portalURL)
    >>> l = browser.getLink(id='specimen-folder')
    >>> l.url.endswith('createObject?type_name=Specimen+Folder')
    True
    >>> l.click()
    >>> browser.getControl(name='title').value = 'Sticky Specimens'
    >>> browser.getControl(name='description').value = 'This folder is just for functional tests.'
    >>> browser.getControl(name='showReferenceSets:boolean').value = True
    >>> browser.getControl(name='showERNELink:boolean').value = True
    >>> browser.getControl(name='form.button.save').click()
    >>> 'sticky-specimens' in portal.objectIds()
    True
    >>> f = portal['sticky-specimens']
    >>> f.title
    'Sticky Specimens'
    >>> f.description
    'This folder is just for functional tests.'
    >>> f.showReferenceSets
    True
    >>> f.showERNELink
    True


Specimens at Site in Protocol
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Inside a Specimen Folder we can add several site records that indicate
specimens at sites that were collected under various protocols.  These are
represented by SpecimensAtSiteInProtocol objects, which can be added solely to
Specimen Folders.  See for yourself::

    >>> browser.open(portalURL)
    >>> browser.getLink(id='specimens-at-site-in-protocol')
    Traceback (most recent call last):
    ...
    LinkNotFoundError

So, let's open up the Specimen Folder we made above and add one there::

    >>> browser.open(portalURL + '/sticky-specimens')
    >>> browser.getLink(id='specimens-at-site-in-protocol').click()
    >>> browser.getControl(name='site:list').displayValue = ["Dr Tongue's 3D Clinic"]
    >>> browser.getControl(name='form.button.save').click()

This object computes its title based on its protocols' title::

    >>> f.objectIds()
    ['dr-tongues-3d-clinic']
    >>> sasip = f['dr-tongues-3d-clinic']
    >>> sasip.Title()
    u"Dr Tongue's 3D Clinic"
    >>> sasip.site.title == sasip.Title()
    True

It also has a total specimen count and participant counts based on each
contained protocol.  Since we don't have any protocols at this site yet, those
totals should be zero::

    >>> sasip.specimenCount
    0
    >>> sasip.participantCount
    0


Specimens in Protocol
~~~~~~~~~~~~~~~~~~~~~

Specimens are collected under the purview of a protocol which guides the
project and all aspects of specimen collection.  These may be created solely
within Specimens at Site in Protocol objects::

    >>> browser.open(portalURL)
    >>> browser.getLink(id='specimens-in-protocol')
    Traceback (most recent call last):
    ...
    LinkNotFoundError

Creating one::

    >>> browser.open(portalURL + '/sticky-specimens/dr-tongues-3d-clinic')
    >>> browser.getLink(id='specimens-in-protocol').click()
    >>> browser.getControl(name='protocol:list').displayValue = ['Public Safety']
    >>> browser.getControl(name='form.button.save').click()

Checking the created object::

    >>> sasip.objectIds()
    ['public-safety']
    >>> sip = sasip['public-safety']
    >>> sip.Title()
    'Public Safety'
    >>> sip.Title() == sip.protocol.title
    True

Did you notice the title of the object?  That's right, it was generated from
the protocol's title.  Also note the specimen and participant counts::

    >>> sip.specimenCount
    0
    >>> sip.participantCount
    0

It's zero because we have no specimen records yet.

Let's add one more Specimens in Protocol object which we can use later::

    >>> browser.open(portalURL + '/sticky-specimens/dr-tongues-3d-clinic')
    >>> browser.getLink(id='specimens-in-protocol').click()
    >>> browser.getControl(name='protocol:list').displayValue = ['Special Ops']
    >>> browser.getControl(name='form.button.save').click()
    

Specimen Record
~~~~~~~~~~~~~~~

A Specimen Record object captures the the counts of specimens and counts of
participants who gave up those specimens For Science (tm).  They may be
created solely within a Specimens in Protocol object::

    >>> browser.open(portalURL)
    >>> browser.getLink(id='specimen-record')
    Traceback (most recent call last):
    ...
    LinkNotFoundError
    >>> browser.open(portalURL + '/sticky-specimens/dr-tongues-3d-clinic/public-safety')
    >>> browser.getLink(id='specimen-record').click()
    >>> browser.getControl(name='specimenCount').value = '123'
    >>> browser.getControl(name='participantCount').value = '46'
    >>> browser.getControl(name='cancerDiagnosis').displayValue = ['With Cancer']
    >>> browser.getControl(name='specimenType').displayValue = ['Blood']
    >>> browser.getControl(name='storageType').displayValue = ['DNA']
    >>> browser.getControl(name='form.button.save').click()

Does it work?  Of course it does::

    >>> sip.objectIds()
    ['123-blood-dna-specimens-at-3d-from-46-with-cancer']
    >>> specRecord1 = sip['123-blood-dna-specimens-at-3d-from-46-with-cancer']
    >>> specRecord1.Title()
    u'123 Blood/DNA Specimens at 3D from 46 with Cancer'
    >>> specRecord1.Description()
    u"Collected at Dr Tongue's 3D Clinic from 46 participants diagnosed with cancer."
    >>> specRecord1.specimenCount
    123
    >>> specRecord1.participantCount
    46
    >>> specRecord1.cancerDiagnosis
    'with'
    >>> specRecord1.specimenType
    '3'
    >>> specRecord1.storageType
    '9'
    >>> specRecord1.siteName()
    "Dr Tongue's 3D Clinic"

OK, that's nice and all, but did making this object update the upward containers?

    >>> sip.specimenCount, sip.participantCount
    (123, 46)
    >>> sasip.specimenCount, sasip.participantCount
    (123, 46)

Great!  Now let's add another record::

    >>> browser.open(portalURL + '/sticky-specimens/dr-tongues-3d-clinic/public-safety')
    >>> browser.getLink(id='specimen-record').click()
    >>> browser.getControl(name='specimenCount').value = '6'
    >>> browser.getControl(name='participantCount').value = '1'
    >>> browser.getControl(name='cancerDiagnosis').displayValue = ['Without Cancer']
    >>> browser.getControl(name='specimenType').displayValue = ['Stool']
    >>> browser.getControl(name='storageType').displayValue = ['Stool homogenate']
    >>> browser.getControl(name='form.button.save').click()

And notice the updates::

    >>> sip.specimenCount, sip.participantCount
    (129, 47)
    >>> sasip.specimenCount, sasip.participantCount
    (129, 47)

Nifty, huh?

TODO: How do we prevent editing of an existing record?  Initial creation is
OK, but subsequently, the object should be read only.


More Updating
~~~~~~~~~~~~~

So far the second protocol we added to Dr Tongue's 3D Clinic hasn't gotten any
love, so let's fix that::

    >>> browser.open(portalURL + '/sticky-specimens/dr-tongues-3d-clinic/special-ops')
    >>> browser.getLink(id='specimen-record').click()
    >>> browser.getControl(name='specimenCount').value = '10'
    >>> browser.getControl(name='participantCount').value = '10'
    >>> browser.getControl(name='cancerDiagnosis').displayValue = ['Without Cancer']
    >>> browser.getControl(name='specimenType').displayValue = ['Stool']
    >>> browser.getControl(name='storageType').displayValue = ['Stool homogenate']
    >>> browser.getControl(name='form.button.save').click()

This shouldn't have affected the Public Safety counts::

    >>> sip.specimenCount, sip.participantCount
    (129, 47)

Good, they're the same as before.  However, it should affect the totals for
the clinic::

    >>> sasip.specimenCount, sasip.participantCount
    (139, 57)

Great.  And what if we drop this newly created record?  Check it out::

    >>> browser.open(portalURL + '/sticky-specimens/dr-tongues-3d-clinic/special-ops/10-stool-stool-homogenate-specimens-at-3d-from-10-without-cancer')
    >>> browser.getLink(id='delete').click()
    >>> browser.getControl('Delete').click()
    >>> sasip.specimenCount, sasip.participantCount
    (129, 47)

Perfect.


Views
-----

Here we'll show how the content types present themselves in a browser.


Specimen Folder
~~~~~~~~~~~~~~~

Specimen Folders sport a nifty view that have a number of features.  Let's
take a look::

    >>> browser.open(portalURL + '/sticky-specimens')

First off, there should be a link to the specimen reference sets::

    >>> browser.contents
    '...http://nohost/plone/resources/sample-reference-sets...'

However, that's configurable.  Let's turn it off::

    >>> browser.getLink('Edit').click()
    >>> browser.getControl(name='showReferenceSets:boolean').value = False
    >>> browser.getControl(name='form.button.save').click()
    >>> 'http://nohost/plone/resources/sample-reference-sets' in browser.contents
    False
    
Secondly, there should be a link to ERNE's user interface::

    >>> browser.contents
    '...https://ginger.fhcrc.org/edrn/imp/GateServlet?pwd=...'
    
Bot that too is configurable::

    >>> browser.getLink('Edit').click()
    >>> browser.getControl(name='showERNELink:boolean').value = False
    >>> browser.getControl(name='form.button.save').click()
    >>> 'https://ginger.fhcrc.org/edrn/imp/GateServlet?pwd=' in browser.contents
    False

Finally, there's a nifty bar chart at the bottom::

    >>> browser.contents
    '...http://chart.apis.google.com...'


Specimens at Site in Protocol
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Objects of the Specimens at Site in Protocol class show each of their
Specimens in Protocol objects in alphabetical order::

    >>> browser.open(portalURL + '/sticky-specimens/dr-tongues-3d-clinic')
    >>> browser.contents
    '...Public Safety...Special Ops...'

That's all there is.


Specimens in Protocol
~~~~~~~~~~~~~~~~~~~~~

Although Specimens in Protocol objects are containers that hold Specimen
Record objects, they don't actually display links to those objects (unless, of
course, you navigate to the Contents tab).  Instead, they display a summary
table of the Specimen Record objects.  They used to have hyperlinks right into
Peter Lin's ERNE UI, but not anymore::

    >>> browser.open(portalURL + '/sticky-specimens/dr-tongues-3d-clinic/public-safety')
    >>> 'https://ginger.fhcrc.org/' in browser.contents
    False

That's good, because now Specimen Records provided their own richly detailed
displays.  Read on to learn about those.


Specimen Record
~~~~~~~~~~~~~~~

Specimen records used to link to ERNE, but that's no longer the case::

    >>> browser.open(portalURL + '/sticky-specimens/dr-tongues-3d-clinic/public-safety/123-blood-dna-specimens-at-3d-from-46-with-cancer')
    >>> 'https://ginger.fhcrc.org/' in browser.contents
    False
    
Now, they show richly detailed data, pulled straight from ERNE!


RDF Ingest
----------

Not supported.  Woot.


.. References:
.. _EKE: http://cancer.jpl.nasa.gov/documents/applications/knowledge-environment
.. _RDF: http://w3.org/RDF/
.. _URI: http://w3.org/Addressing/
