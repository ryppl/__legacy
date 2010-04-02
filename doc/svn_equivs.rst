.. highlight:: git_shell

SVN Command equivalents
=======================

svn cat
-------

``svn cat boost/version.hpp``

  git show HEAD:boost/version.hpp

The ``HEAD`` here is the revision of the current branch.  So ``svn cat
-r PREV boost/version.hpp`` would be ::
 
  git show HEAD^:boost/version.hpp

and the version three revisions ago ::

  git show HEAD~3:boost/version.hpp 
  
svn revert
----------

``svn revert boost/version.hpp`` ::

  git checkout boost/version.hpp

This removes any local changes to a file and replaces them with the
last-committed version.  

