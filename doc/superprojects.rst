Superprojects
:::::::::::::

Ryppl superprojects (we expect Boost_ to be one) are simply projects
that aggregate other Ryppl projects as Git submodules.  In addition,
they usually have some superproject-specific content of their own.
Note that it's usually not appropriate to express ordinary Ryppl
project dependencies as subprojects; the distinguishing difference is
that superprojects actually expose their subprojects to the
superproject's users as first-class components, rather than simply
relying on the subprojects as implementation details.

Release
=======

Because Git submodules are actually pointers to a specific revision in
a specific repository, the superproject maintainer has precise control
over which version of each subproject is released.  Normally a
superproject release will point at the latest releasable state of each
subproject, but it's perfectly easy to choose an earlier releasable
state, or even, as a last resort, create a fork of the subproject and
use that.  Because it's Git, reconciling a fork with upstream
development is easy.

.. _Boost: http://www.boost.org

Testing
=======

The main goal of superproject testing is to ensure that the released
states of all subprojects are compatible.

TODO: write more
