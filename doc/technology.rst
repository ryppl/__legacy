Technologies
============

Ryppl relies on the following technologies:

* Python_ 2.x
* Git_
* CMake_

.. _Python: http://python.org
.. _Git: http://git-scm.com
.. _CMake: http://cmake.org

You don't need to know Python at all to use Ryppl; it's just an
implementation language.  You also don't need to know Git… unless you
are going to be doing development work on Ryppl projects.  Ryppl
projects are always managed via Git repositories.  If you really must
use a different SCM for real development work, there are ways to link
Git with most popular SCMs.

Learning about Git
------------------

The quick skinny on Git_, if you don't already know, is that it is a
distributed revision control system that uses copy-on-write and
preserves object identities across clones of a repository.  What does
that mean for you?  

* **Distributed** means that every working copy of a project has a
  subdirectory containing a repository that holds *at least* the
  complete development history up to that working copy state.

* **Copy-on-write** means that no data is ever destroyed, as long as
  it can be referenced, and Git can store commits and all their
  ancestors as objects.

* **Object identities** that persist across repositories means that
  when you pull someone else's work into your repository, any history
  that work shares with what your repository contains is automatically
  and reliably recognized, and used.  Each repository actually
  contains a subset of a potentially larger DAG of commits and merges.
  
If you need to know more and you're just getting started with Git,
pick up `Pro Git <http://progit.org/book>`_ and watch `Contributing
with Git <http://www.youtube.com/watch?v=j45cs5_nY2k>`_, Johannes
Schindelin's introductory Google Tech Talk.

Internals and Other Resources
.............................

* `Git from the bottom up <http://ftp.newartisans.com/pub/git.from.bottom.up.pdf>`_ (See also the links at the end of this document).
* `Git for Computer Scientists <http://eagain.net/articles/git-for-computer-scientists/>`_
* `Git home page <http://git-scm.com>`_
* `hub <http://github.com/defunkt/hub>`_: convenient shorthands for working with `GitHub <http://github.com>`_.

Information on Git Submodules
.............................

* http://www.kernel.org/pub/software/scm/git/docs/git-submodule.html
* http://woss.name/blog/2008/4/9/using-git-submodules-to-track-plugins.html
* http://git.or.cz/gitwiki/GitSubmoduleTutorial
* http://gaarai.com/2009/04/20/git-submodules-adding-using-removing-and-updating/
* http://progit.org/book/ch6-6.html

