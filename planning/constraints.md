# ADA
Applications put forth by QPSI must be ADA compliant.
This is noteworthy here due to the interactive visualizations.

One option that is being considered is to insert only the interactive elements as iFrames in the notebook's page in UF QPSI https://knowledge.qpsi.med.ufl.edu/ .
The downside of this is that the notebook would not be all together if we wanted to serve it by itself sometime.

Another option would be to figure out some ADA compliant solution while still having the whole notebook intact.
I wonder if we could put the whole notebook in the iFrame and the ADA-compliant systems could crawl through that?
This would be nice :)


## New ADA/accessibilty guidance from QPSI team member:
This looks great, Sasank! I’ve done some preliminary research, and we’d have some considerable work to make the interactive charts compliant from an accessibility perspective. Here are a few of the biggest items:

- Output charts as SVG as much as possible instead of as a canvas element.
- Provide table versions of charts. These could be something that gets toggled on or off if we don’t want to clutter the view for sighted users.
- Make sure inputs for charts can be accessed and updated by keyboard (ie - user can tab to the controls and update values with keyboard)
- Aria-live, aria-atomic, and aria-relevant attributes should be used where a chart changes. This could be a hidden element that summarizes the data to the screen reader when a relevant change is made to the chart.

We’d need to check on a couple of other minor items, but these are the biggest hurdles for implementation.








# Maintainability
Must be easy to maintain.






