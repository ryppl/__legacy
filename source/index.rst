.. highlight:: git_shell

.. _contents:

Hacking Boost via Git
=====================

As of this writing (|today|) this is not *yet* a proposal to switch
main source control for boost away from subversion to git.  In the
meantime, this evolving document intends to

* provide a demonstration of the system and a "try it out" process for
  the curious
* propose a superior alternative to current sandbox/vault practice
* establish best practices for those who are already hacking boost via
  git
* serve as a reference point for discussion and experimentation

.. rubric:: Highly recommended reading:

Thanks to the folks on freenode's #git:

* `Git from the bottom up <http://ftp.newartisans.com/pub/git.from.bottom.up.pdf>`_ (See also the links at the end of this document).
* `Git for Computer Scientists <http://eagain.net/articles/git-for-computer-scientists/>`_
* `Git home page <http://git-scm.com>`_

.. rubric:: YouTube:

* `Linus Torvalds on Git <http://www.youtube.com/watch?v=4XpnKHJAok8>`_ the now famous Google
  Tech Talk.  A must-watch.
* `Contributing with Git
  <http://www.youtube.com/watch?v=j45cs5_nY2k>`_ Johannes Schindelin's
  Google Tech Talk.  Good for beginners.

Contents
========

.. toctree::
   :maxdepth: 3

   setup
   development
   subversion
   svn_equivs
   various_howtos
   about_the_mirror
   



About this documentation
========================

This documentation is written in `reStructuredText
<http://docutils.sourceforge.net/rst.html>`_ and assembled by `Sphinx
<http://sphinx.pocoo.org>`_.  You can get the source from the
``boost-git-docs`` branch of the git repository at
``git://sodium.resophonic.com/boost_cookbook``.  

.. rubric:: Why does the logo at the top say *unauthorized*?

Because the content is neither official boost (ie having passed
code review and been accepted) nor *proposed*.  I suppose I could
have used "fringe" as well.

