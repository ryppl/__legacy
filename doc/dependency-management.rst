Dependency Management
=====================

The Graph
---------

This configuration of dependencies should be enough to uncover many of the edge cases.

.. digraph:: lib_dependencies

   "libA" -> "libC"
   "libA" -> "libX"
   "libB" -> "libX"
   "proj" -> "libA"
   "proj" -> "libB"

   
*proj* is a project that might not be hosted at ryppl. *libA*, *libB*,
*libC*, and *libX* are ryppl library projects.

.. Admonition:: Question

   Can we simplify the diagram without losing important cases by
   adding an arc from *proj* to *libX* and dropping *libB* altogether?

Specifics of Setup
------------------

The developer of *libA* has a .ryppl file to his project at the top level::

  depends libX:1.0-2.2,3.1
  depends libC

This specifies a dependency on a version of libX numbered 1.0 through
2.2 or numbered 3.1.  

.. Note:: We will need a rule for decoding and comparing version
   names/numbers.  Likely it will need to cover more complicated
   versions like 1.1b2, etc.

*libB* has a similar .ryppl file::

  depends libX:2.0-2.5,3.0

The person developing *proj* does:

::

  ~/proj% ryppl get libA libB

This will pull down the latest release of *libA*, *libB*, and *libC* and version 2.2 of *libX*, since it's the latest version
compatible with both the latest *libA* and *libB*.

Alternatively, the developer of *proj* can have his own .ryppl file::

  depends libA libB

and simply execute::

  ~/proj% ryppl

In case of conflicts,where the latest *libA* and *libB* are not
compatible with any common version of *libX*, the user should be offered options

* Abort
* Look for earlier versions of *libA* and *libB* that are compatible
* Fall back to a guess about a compatible *libX*

The default assumption should be that later versions don't break
backward-compatibility, so a project that depends on v2.0 of *libX*
will also work with v3.0.

Events
------

Now we'll look at a number of things that might happen.  A set of
changes to be applied will be referred to here as a “patch,” even if
not expressed or completely expressible as a patch file.

Developer Update
::::::::::::::::

Library developer propagates a patch “downstream” (from library
dependency to dependent project).  Propagation can either be 

* a **release**, where a patch becomes part of one or more named
  categories of updates (e.g. “critical update,” “beta,” “version
  upgrade,” etc.) known as a *release branch* that can be subscribed
  to by users and automatically applied.

* a **downstream test request**, where specific users are asked to try
  a patch, but it is not “released” for general consumption.  The
  patch gets its own name and is not (yet) part of a release branch.

Downstream patch propagation will cause some automatic source merging
when downstream subscribers.  Some of the (likely) working tree states being
employed by users may be known to the upstream developer, e.g. the
HEADs of any release branches are likely candidates.  

*Ideally* we'd like to (optionally) automatically test compatibility
of any patch with these known downstream states at two levels—a test
for a clean merge or a full regression test—but these don't seem like
“priority 1” features.  

Regardless, downstream merges will sometimes fail, or fail to work.
In these cases, it is crucial that downstream users' working tree
states are restored.  Such failures should be automatically reported
upstream in a way that allows the upstream developer to correct them.

User Update
:::::::::::

The developer of *proj* patches one of the libraries on which *proj*
depends.  

The change will be checked into the user's repository, and persists
there until integrated upstream.  Upstream integration works as
follows:

1. Ryppl locates the nearest ancestor of user's working state that
   exists in developer's repo and creates a patch branch there.

2. Ryppl applies patch to patch branch

3. Ryppl switches user to patch branch and rebases any other user
   changes.

This should all happen without modification of user's patch.  

If developer wants to make modifications before merging back into a
release branch, she is free to do so, but this should be done as
follow-up checkins on the patch branch, and requests for a
pull+update+test should be sent automatically to user.

Merge to release branch should similarly automatically notify user,
with the option for automatic or manual switching of user's working
tree state to the release branch.
