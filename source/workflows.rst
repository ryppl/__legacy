
.. highlight:: git_shell

Use Cases
:::::::::

This section describes cases that need to be handled by this system,
not just for library developers, but for end-users, integrators, etc.
These use cases are not currently prioritized.  We divide them by the
role of the initiator.

Fundamentals
============

We expect the following tasks to be done frequently by (relatively)
non-technical people, so we intend them to be **dead simple.**

Tool Installation
-----------------

Installation of the ryppl tools should be a single command with
interactive steps as necessary.  Maybe this is just part of what
happens every time the ryppl command is run:

.. parsed-literal::

  $ ryppl *whatever*
  I couldn't find Git in your path.  Type the path to a Git executable
  here [default: I'll install one for you]:

Ryppl will need a place to check out packages; call this a “ryppl
workspace.”  The Cygwin binary installer's package directory selection
provides a nearly perfect model: you can say “download from internet,”
which means you don't really care where it puts the package files, or
you can supply a path.

Non-technical users who are installing software will typically choose
“download from internet.”  Anyone doing development will typically
choose a location for packages.  Invoking ``ryppl`` from within a
ryppl workspace simply uses that workspace.

Package Installation
--------------------

In the simplest case, the user wants to install some software and
doesn't care about required intermediate steps, e.g. compilation and
testing.  The *dead-simple command* is:

.. parsed-literal::

   $ ryppl install *project1* *project2* *project3*\ …

With testing prior to installation:

.. parsed-literal::

   $ ryppl install --test *project1* *project2* *project3*\ …

Development
-----------

* Maintainer stored per project
* Prepare to hack on an existing Ryppl project
* Check in changes an existing Ryppl project
* Prepare to hack on a new Ryppl project
* Publish changes to the world
* Request that maintainer merge changes
* Mark a commit as a releasable state
* Review outstanding merge requests
* Speculative test requests
  - platform/branch specificity
  - auto-notification of results
  - auto-adjustment of “releasable” tag


Testing
-------

- Incremental testing is absolutely required.
- Releasability tests combine testing results with expected failure markup.
- Expected failure markup is stored per-library.
- Notifications initially via email

* Summary of a project's releasability criteria
* Test these three Ryppl projects
* Test these three Ryppl projects and whatever they depend on
* Test a superproject (like Boost)
* Prepare a testing slave machine
  * Subset of projects
  * Subset of public repos/developers to pull from
* Subscribe to test results

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


