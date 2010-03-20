.. highlight:: git_shell

.. _contents:


.. raw:: html

  <a href="http://sourceforge.net/donate/index.php?group_id=311126"><img src="http://images.sourceforge.net/images/project-support.jpg" width="88" height="32" border="0" alt="Support This Project" /> </a>

Distributed Development, Testing and Installation with Ryppl
============================================================

.. toctree::
   :maxdepth: 3

   workflows
   dependency-management
   gettingstarted
   modifying_the_python_lib
   svn_equivs
   various_howtos
   design-details


Overview
--------

Think of Ryppl as a `package management system
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

Learning about Git
------------------

* `Pro Git <http://progit.org/book>`_.
* `Contributing with Git
  <http://www.youtube.com/watch?v=j45cs5_nY2k>`_ Johannes Schindelin's
  Google Tech Talk Video.  Good for beginners.

Internals and Other Resources
.............................

* `Git from the bottom up <http://ftp.newartisans.com/pub/git.from.bottom.up.pdf>`_ (See also the links at the end of this document).
* `Git for Computer Scientists <http://eagain.net/articles/git-for-computer-scientists/>`_
* `Git home page <http://git-scm.com>`_
* `hub <http://github.com/defunkt/hub>`_: convenient shorthands for working with `GitHub <http://github.com>`_.

Information on Git Submodules
-----------------------------

* http://www.kernel.org/pub/software/scm/git/docs/git-submodule.html
* http://woss.name/blog/2008/4/9/using-git-submodules-to-track-plugins.html
* http://git.or.cz/gitwiki/GitSubmoduleTutorial
* http://gaarai.com/2009/04/20/git-submodules-adding-using-removing-and-updating/
* http://progit.org/book/ch6-6.html


