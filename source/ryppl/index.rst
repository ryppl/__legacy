.. highlight:: git_shell

Ryppl: a prototype
==================

It's *Ryppl* pronounced "ripple".  Currently the *mainline* of ryppl
contains a reorganized ``boost.cmake 1.41.0``.  Projects *wave* and
*python* have been "modularized", ie they are not contained in the
ryppl subdirectory but are brought in via git submodules. Three useful
sandbox projects have been added, as modules: *chrono*, *process*,
and *fiber*.  

For experimentation purposes, the repository **straszheims-python**
contains Straszheim's boost.python branch, containing a number of new
features and bugfixes.  The respository **straszheims-ryppl** contains
a clone of ryppl with the submodules updated to use
**straszheims-python**.

These repositories are all to be found in
http://gitorious.org/ryppl.  This documentation is in repository
``doc``.

.. rubric:: Contents

.. toctree::
   :maxdepth: 3

   gettingstarted
   highlevelscenarios
   scenarios



  
Good Links
==========

* http://www.kernel.org/pub/software/scm/git/docs/git-submodule.html
* http://woss.name/blog/2008/4/9/using-git-submodules-to-track-plugins.html
* http://git.or.cz/gitwiki/GitSubmoduleTutorial
* http://gaarai.com/2009/04/20/git-submodules-adding-using-removing-and-updating/
* http://progit.org/book/ch6-6.html

