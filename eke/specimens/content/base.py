# encoding: utf-8
# Copyright 2010 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''EDRN Knowledge Environment Specimens: content base implementations and common features.'''

from eke.specimens import ProjectMessageFactory as _
from Products.Archetypes import atapi

# Schema for ISpecimenStatistics: specimen count.
CountsSchema = atapi.Schema((
    atapi.IntegerField(
        'specimenCount',
        required=True,
        default=0,
        searchable=False,
        storage=atapi.AnnotationStorage(),
        widget=atapi.IntegerWidget(
            label=_(u'Specimen Count'),
            description=_(u'How many individual specimens have been collected.'),
            visible={'edit': 'visible', 'view': 'visible'},
        ),
    ),
))
