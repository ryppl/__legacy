
Committing back to subversion
=============================

I have a clean updated svn trunk checkout at ``/tmp/svn``.  I'm in git
and have some local changes.  As an example I'll pull some
``CMakeLists.txt`` over from the release branch to the trunk::

  % git checkout svn/release libs/flyweight/CMakeLists.txt libs/flyweight/test/CMakeLists.txt CMakeLists.txt
  % git add libs/flyweight/CMakeLists.txt libs/flyweight/test/CMakeLists.txt CMakeLists.txt
  % git status
  # On branch mytweaks
  # Changes to be committed:
  #   (use "git reset HEAD <file>..." to unstage)
  #
  #       modified:   CMakeLists.txt
  #       new file:   libs/flyweight/CMakeLists.txt
  #       new file:   libs/flyweight/test/CMakeLists.txt
  #
  % git commit -m "moving cmakefiles release->trunk"
 
You can easily format a patch to transform the svn trunk into your current branch::

  % git diff -p svn/master
  diff --git a/CMakeLists.txt b/CMakeLists.txt
  index 5e521ad..e4ddc93 100644
  --- a/CMakeLists.txt
  +++ b/CMakeLists.txt
  @@ -27,40 +27,28 @@
   cmake_minimum_required(VERSION 2.6.0 FATAL_ERROR)
   project(Boost)

  (etc etc) 
  
Now to apply to svn.  [#quickpatch]_ Note that the patch above has
leading paths a/ and b/; for this reason you need the flag ``-p1`` to
have ``patch`` strip the first pathname component::

  % git diff -p svn/master > /tmp/svn/cmake.patch
  % cd /tmp/svn 
  % patch -p1 < cmake.patch
  patching file CMakeLists.txt
  patching file libs/flyweight/CMakeLists.txt
  patching file libs/flyweight/test/CMakeLists.txt

Note that if the patch adds or removes files, svn won't be told it
should commit them::

  % svn status
  ?      libs/flyweight/CMakeLists.txt
  ?      libs/flyweight/test/CMakeLists.txt
  M      CMakeLists.txt
  
(nor will file permissions, etc, be handled).  You'll have to
add/remove these files by hand with ``svn add`` and ``svn rm``, e.g.::

  % svn rm `svn status | grep ^! | awk '{ print $2 }'` 
  D         tools/build/CMake/BoostBuildSlave.cmake
  D         tools/build/CMake/run_continuous_slave.py.in
  D         tools/build/CMake/post.py.in
  % svn add `svn status | grep ^\? | awk '{ print $2 }'` 
  A         CTestConfig.cmake

And then commit at will.  The commits will work their way through
subversion, to the upstream git, to the gitorious mirror, and into
your codebase at your next fetch/merge/pull.

Note that the process is a little lossy as various git commits become
one svn commit with a possibly different comment.  You can use :command:`git 
format-patch` to make a bunch of patch files containing commit messages,
like this::

  % git format-patch svn/master
  0001-.patch
  0002-.patch
  0003-.patch

  % cat 0001-.patch 
  From 559336b1b4666db55c2c78d3ee11fff47b552cf0 Mon Sep 17 00:00:00 2001
  From: troy <troy@resophonic.com>
  Date: Fri, 24 Apr 2009 10:41:07 -0400
  Subject: [PATCH] Stop compiler warnings
  
  ---
   libs/serialization/src/basic_xml_grammar.ipp |    6 +++---
   1 files changed, 3 insertions(+), 3 deletions(-)
  
  diff --git a/libs/serialization/src/basic_xml_grammar.ipp b/libs/serialization/src/basic_xml_grammar.ipp
  index 07dc9a5..103af9d 100644
  --- a/libs/serialization/src/basic_xml_grammar.ipp
  +++ b/libs/serialization/src/basic_xml_grammar.ipp
  @@ -17,9 +17,9 @@
   #include <boost/config.hpp> // BOOST_DEDUCED_TYPENAME
   
   // spirit stuff
  -#include <boost/spirit/core/composite/operators.hpp>
  -#include <boost/spirit/core/composite/actions.hpp>
  
Buuuut svn doesn't know what to do with these things.  I suppose you'd
have to write a little script to apply the patches and commit them
with their original log messages.  


.. rubric:: Footnotes

.. [#quickpatch] A quicker way, if you keep a clean subversion
   		 checkout laying around in :file:`/tmp/svn`:
   		 ``git diff origin/release | (cd /tmp/svn ;
   		 patch -p1)``

