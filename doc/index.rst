.. highlight:: git_shell

.. _contents: On This Page

Distributed Development, Testing and Installation with Ryppl
============================================================


Overview
--------

Think of Ryppl as a cross-platform [#platforms]_ `package management system
<http://en.wikipedia.org/wiki/Package_management_system>`_ designed to
accomodate both end-users *and* developers.  Unlike a traditional
package manager, which delivers binaries and/or a source snapshot,
when ryppl downloads a package, it gives you a clone of a Git
repository, with that package's entire development history.  If you're
an ordinary end-user, the fact that it's a git repository may be
invisible to you, but if you're a developer, it means you're already
prepared to work on the package, keep track of your changes, and
submit them to the official maintainer(s).

Ryppl includes facilities for building, testing, and installing
packages on the local machine.  However, it also has integrated
support for *remote* testing.  That is, you can arrange that tests be
run on build slaves located “out there” on the internet. This allows
developers to discover portability issues without having direct access
to every build platform.

About this documentation
------------------------

This documentation is written in `reStructuredText
<http://docutils.sourceforge.net/rst.html>`_ and assembled by `Sphinx
<http://sphinx.pocoo.org>`_.  You can get the source from the
``doc/`` subdirectory of the ``master`` branch of the git repository at
``git://github.com/ryppl/ryppl.git``.  

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


Full Table Of Contents
----------------------

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


---------

.. [#platforms] Ryppl works on Windows and Posix systems.
