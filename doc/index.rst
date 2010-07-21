.. highlight:: git_shell

.. _contents: On This Page

Distributed Development, Testing and Installation with Ryppl
============================================================


Overview
--------

Think of Ryppl as a distributed cross-platform software management
system designed to accommodate both end-users and developers. Ryppl
unites version control, test management, `package management
<http://en.wikipedia.org/wiki/Package_management_system>`_ , release
management, reporting, and other sub-systems into a coherent and
scalable software management system.

Unlike a traditional package manager, which only delivers binaries
and/or a source snapshot, when ryppl downloads a package, it can give
you a clone of a Git repository, with that package's entire
development history.  If you're an ordinary end-user, the fact that
it's a git repository may be invisible to you, but if you're a
developer, it means you're already prepared to work on the package,
keep track of your changes, and submit them to the official
maintainer(s).

Ryppl includes facilities for building, testing, and installing
packages on the local machine.  However, it also has integrated
support for *remote* testing.  That is, you can arrange that tests be
run on build slaves located “out there” on the internet. This allows
developers to discover portability issues without having direct access
to every build platform.

Resources
---------

* `Source Code on GitHub <http://github.com/ryppl>`_
* `Issue Tracker <http://github.com/ryppl/ryppl/issues>`_
* Dave Abrahams' rough `ryppl slideset from BoostCon 2010
  <http://www.filetolink.com/c644b59c>`_ (outdated, but correct in
  spirit)
* `Ryppl development mailing list <http://groups.google.com/group/ryppl-dev>`_
* #ryppl IRC channel at irc.freenode.net
* `Issue Tracker <http://github.com/ryppl/ryppl/issues>`_
* `Source Code <http://github.org/ryppl/ryppl>`_
* `README <http://github.com/ryppl/ryppl#readme>`_ for Ryppl developers
* David Cole's `CMake slideset from BoostCon 2010 <http://www.filetolink.com/0135fa83>`_

Status as of 2010-06-22
-----------------------

Functionality
.............

What we can do currently:

* Accept a request to get a project, optionally a specific version
* Look up a project in the project index (a simple website) and find its Git repository.
* Find the versions of that project based on tags in the Git repository
* Read the project's metadata file to find its dependencies (and their
  version requirements)
* Recursively clone repositories for the project and all of its
  dependencies at the appropriate version (subject to some limitations
  ATM: http://bitbucket.org/ianb/pip/issue/119)

Code
....

At the time of this writing, the `code in Ryppl itself
<http://github.com/ryppl/ryppl/tree/master/src/ryppl>`_ is just an
extraordinarily thin layer over PIP and Distutils2… which is how we
want things.  The idea is to *not* end up with a system that requires
much in the way of its own maintenance.

Momentum
........

A huge effort was expended April-May 2010 to get `pip
<http://pip.openplans.org>`_ to work properly on Windows and to be
hookable with our functionality.  Development went into a slight lull
(to accommodate other work) in late June 2010, but Eric Niebler is
actually moving his physical address to Cambridge, MA on July 1 to
work side-by-side, and essentially full-time, with Dave Abrahams on
ryppl.  Expect a large burst of progress then.

Also, Kitware has committed a *minimum* of one full man-month over the
period ending May 2011 to getting all necessary CMake_ (and
CTest/CDash) support in place.

.. _CMake: http://cmake.org

Support This Project
--------------------

.. raw:: html

   <div class="pledgie" style="float:right">
          <a href="http://pledgie.com/campaigns/9508"><img alt="Click here to lend your support to: ryppl and make a donation at www.pledgie.com !" src="http://www.pledgie.com/campaigns/9508.png?skin_name=chrome" border="0"></a>
        </div>

Most contributors are giving their time to this project for free.  If
you make a donation to Ryppl, it will be used to pay for the time of
those who can't afford to be quite so generous.  We need their help,
and they need to pay the bills, so please consider `making a donation
<http://pledgie.com/campaigns/9508>`_.  Thanks!


Sections
--------

.. toctree:: 
   :maxdepth: 3

   technology
   workflows
   dependency-management
   superprojects
   gettingstarted
   modifying_the_python_lib
   svn_equivs
   various_howtos
   design-details


About this documentation
------------------------

This documentation is written in `reStructuredText
<http://docutils.sourceforge.net/rst.html>`_ and assembled by `Sphinx
<http://sphinx.pocoo.org>`_.  You can get the source from the
``doc/`` subdirectory of the ``master`` branch of the git repository at
``git://github.com/ryppl/ryppl.git``.  


---------

.. [#platforms] Ryppl works on Windows and Posix systems.
