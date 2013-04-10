## Script (Python) "compute_participants"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=item=None
##title=Find out if the object is expired
##

if item is None:
    return 0

value = item.getNumParticipants
if not value:
    # Is the value really zero?
    specimenSet = item.getObject()
    actualValue = specimenSet.getNumParticipants()
    if actualValue == 0:
        # It really is zero. Wow.
        return 0
    # Ah ha. Reindex this individual specimen set so the "getNumParticipants" column gets fixed.
    specimenSet.reindexObject()
    return actualValue
# Oh goodness gracious me, the column had a useful value!
return value
