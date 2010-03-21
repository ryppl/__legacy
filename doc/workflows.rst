
.. highlight:: git_shell

Workflows
:::::::::

This section describes cases that need to be handled by this system,
not just for library developers, but for end-users, integrators, etc.
These use cases are not currently prioritized.  We divide them by the
role of the initiator.

Conventions
-----------

Most `ryppl` commands take the form:

.. parsed-literal::

  ryppl *command-name* [ *options*\ … ] [ *project-names*\ … ]

If no *project-names* are supplied, such commands expect your current
directory to be in the working tree of a Ryppl project, and that you
intend to operate on that project.

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
===========

Things done by software developers.

Getting the Source
------------------

To get the source for an existing ryppl project, start by pulling the
code down from the official repository:

.. parsed-literal::

   $ ryppl checkout *project*

that puts the source for *project* in a subdirectory called *project/*
of your ryppl workspace.  You now have a Git repository in which to
work.  To commit changes locally, simply use regular Git commands in
the project subdirectory (or a child).  Most ryppl commands described
in the Development_ section are documented with the assumption that
the current directory is the project subdirectory or a child thereof.

If you are a maintainer, ryppl will detect that fact.  Otherwise, most
likely you will want to create a public repository where you can
publish your changes.  You can wait until you actually want to
publish, but you may find that you are more inclined to push changes
out (and thus create a non-local backup of your work) if the
repository is already prepared.  See `Publishing Projects`_ for
details.

Publishing Projects
-------------------

To make your project visible to the world,

.. parsed-literal::

   $ ryppl publish *project*

Ryppl will dump instructions for creating a public clone of the
official repository. [#siteclone]_

.. Admonition:: Open Question

   GitHub_ and Gitorious_ don't reveal the push URL unless you have
   write permission on the repository. Is there some security concern
   there? Push URLs are easily deduced from the other ones.

.. _Gitorious: http://gitorious.org
.. _GitHub: http://github.com

Merge Requests
--------------

To request that a project maintainer merge your changes into the
project's official repository,

::

  $ ryppl merge-request

will generate an email to the project maintainer containing
instructions for getting and merging your code, giving you an
opportunity to edit the message. [#api]_

Creating a Release
------------------

If you are a project maintainer, it is up to you to decide when the
project can be released.  Releases are created by tagging revisions in
your Git repository.  To release your current working tree, simply

::

  $ ryppl release

If you are working on a branch other than your mainline (usually
``master``), you'll create a point release or a pre-release
(e.g. beta).  You can add an explicit version string, or ryppl will
attempt to assign one for you.

Review Outstanding Merge Requests
---------------------------------

Initially, merge requests can be tracked in the maintainers' own
personal email systems.  At some point we may want to keep track of
which merge requests are unhandled, so a maintainer can ask, ::

  $ ryppl show merge-requests

[This is a low-priority feature.]

Testing
=======

To test a Ryppl project on the local machine from within its project
directory, simply::

  $ ryppl test

Testing Specific Projects
-------------------------

Testing specific Ryppl projects is just as easy:

.. parsed-literal::

   $ ryppl test *project1*\ , *project2*\ … 

Testing Dependencies
--------------------

To also test all the projects that a given list of projects depends on
(transitively):

.. parsed-literal::

   $ ryppl test --deep *project1*\ , *project2*\ … 

Remote Testing
--------------

One of ryppl's most important features is the ability for anyone to
dedicate testing resources to a project.  That allows testing on
diverse platforms not controlled by the project maintainer.  To
test remotely, simply::

  $ ryppl remote-test 

which will request results from your “usual” set of platforms for the
HEAD of the current working tree.  If you have made changes to the
current working tree that aren't checked in, you'll be warned first.
Test result notification emails include a ryppl command-line that the
maintainer can use to release the tested state.

To test on specific slaves, they can be named on the command-line:

.. parsed-literal::

  $ ryppl remote-test --slave=\ *slave1*,\ *slave2*\, …

Test Slave Aliases
------------------

In ``.ryppl/slave-aliases`` at the project root (and in the user's
home directory), one can define aliases for test slaves and pools
thereof.  Each test slave is identified by a unique key that we'll
generate somehow::

      troymac:      19fa345c9732d5
      bemanppcmac:  92d831e63b4572
      davemac:      29831d6eb354c7
      mac:          troymac, bemanppcmac, davemac, 9a1f3c7923dc

Slaves can be identified either by unique key or by alias.  In the
example above, ``mac`` is an alias for a pool of four machines,
presumably all Apple Macs.  Ryppl will choose among these slaves or
(eventually) distribute the tests among them, based on current
workload.  The special slave alias ``default`` defines the slaves to
use when no other slaves are specified.

Setting up a Test Slave
-----------------------

* Subset of projects
* Subset of public repos/developers to pull from

Subscribing to Test Results
--------------------------- 


.. What's Missing

    * Dependency Management - probably independent from CMake
    * Testing is busted?  Yes, for Python.
    * Testing is unweildy (having to call ctest)

    * if we want to use CDash, makes sense to have CTest run tests.
      Incremental testing needs research in that case.


Releasability
-------------

Every project has a file .ryppl/releasability.xml [#xml]_ that
describes the criteria for a project's releasability in terms of which
tests pass on particular test slave aliases.  The file format is, at
least initially, based on the `format
<https://svn.boost.org/trac/boost/browser/trunk/status/explicit-failures.xsd>`_
of `Boost's corresponding file
<https://svn.boost.org/trac/boost/browser/trunk/status/explicit-failures-markup.xml>`_

To summarize a project's releasability criteria, ::

  $ ryppl show release-criteria

[This is a low-priority feature.]


Packaging / Release
===================

* Releasability overview (email)
* Automatically notify maintainers of breakage (email).  Show test /failures/
* Nightly Auto-tagged releasable branch for each library
* Continuous testing of the release branch
* Make binaries


.. [#siteclone] If the official repository is hosted on Gitorious_ or
    GitHub_, these instructions will include directions for cloning
    the repository on the site itself, which enables some cool
    tracking features.

.. [#api] If the repository host has an API that allows such requests
   to be generated (e.g. as GitHub_ does), we may eventually use that
   API where appropriate, but it's not a high priority.

.. [#xml] I'm not attached to XML and we could easily allow other
   formats as well.  XML makes the transition easier for Boost,
   though.
