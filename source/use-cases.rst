
.. highlight:: git_shell

Use Cases
=========

This section describes cases that need to be handled by this system,
not just for library developers, but for end-users, integrators, etc.
These use cases are not currently prioritized.  We divide them by the
role of the initiator.

Installation
------------

* Get set up to use Ryppl

User
----

* Get these three Boost libraries (and whatever they depend on)
* Resolve version dependency conflicts
* Summary of a project's releasability criteria

Testing
-------

Incremental testing is absolutely required.
Releasability tests combine testing results with expected failure markup.
Expected failure markup is stored per-library.

* Test these three Ryppl projects
* Test these three Ryppl projects and whatever they depend on
* Test a superproject (like Boost)
* Prepare a testing slave machine
  * Subset of projects
  * Subset of public repos/developers to pull from
* Subscribe to test results

Development
-----------

* Maintainer stored per project
* Prepare to hack on an existing Ryppl project
* Check in changes an existing Ryppl project
* Prepare to hack on a new Ryppl project
* Publish changes to the world
* Request that maintainer merge changes
* Review outstanding merge requests
* Speculative test requests
  * platform/branch specificity
  * auto-notification of results

.. What's Missing

    * Dependency Management - probably independent from CMake
    * Testing is busted?  Yes, for Python.
    * Testing is unweildy (having to call ctest)

    * if we want to use CDash, makes sense to have CTest run tests.
      Incremental testing needs research in that case.

Packaging / Release
-------------------

* Releasability overview (email)
* Automatically notify maintainers of breakage (email).  Show test /failures/
* Nightly Auto-tagged releasable branch for each library
* Continuous testing of the release branch
* Make binaries


