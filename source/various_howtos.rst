Various HOWTOS
==============

Diff trunk and release
----------------------

This is rather time consuming with subversion (I don't seem to be able
to do it at all, apparently due to network timeouts):
  
**SVN version**::
  
    % svn diff http://svn.boost.org/svn/boost/branches/release http://svn.boost.org/svn/boost/trunk > svndiff
    svn: Caught signal
    svn: Error reading spooled REPORT request response
    [1]  + exit 1     svn diff http://svn.boost.org/svn/boost/branches/release  > svndiff
      
**GIT version** (sooooo fast)::
  
    % git diff --stat svn/release svn/master
    CMakeLists.txt                                     |   66 +-
    CTestConfig.cmake                                  |    2 +-
    Welcome.txt                                        |    7 +
    boost-build.jam                                    |    1 +
    boost/aligned_storage.hpp                          |   25 +-
    ...
    tools/release/snapshot_windows.sh                  |   23 +-
    tools/release/strftime.cpp                         |   68 +
    tools/wave/cpp.cpp                                 |    6 +-
    3416 files changed, 199432 insertions(+), 56085 deletions(-)

    % time git diff svn/release svn/master > /dev/null
    git diff svn/release svn/master > /dev/null  0.81s user 0.03s system 100% cpu 0.839 total

  That's a big diff.
  
Track a particular branch
-------------------------

The main repository's branch namespace is badly polluted.  Say you're
interested in playing with things on the cpp0x branch.  This is
mirrored over in the sodium.resophonic.com repository (this could also
be mirrored to gitorious).  In your clone (it doesn't need to have
started with a clone from sodium.resophonic.com, a gitosis one will do).
First find the interesting branch with ``ls-remote`` and ``grep``::

  % git ls-remote git://sodium.resophonic.com/boost | grep cpp
  c65edc0dce094b990b55955ed9dd1ede1885d360        refs/heads/cpp0x

And add the remote, specifying the branch::

  % git add remote sodium git://sodium.resophonic.com/boost -t cpp0x

Fetch yourself the changes::

  % git fetch sodium
  remote: Counting objects: 371, done.
  remote: Compressing objects: 100% (131/131), done.
  remote: Total 270 (delta 192), reused 208 (delta 138)
  Receiving objects: 100% (270/270), 95.71 KiB, done.
  Resolving deltas: 100% (192/192), completed with 35 local objects.
  From git://sodium.resophonic.com/boost
   * [new branch]      cpp0x      -> sodium/cpp0x

Check it out and see what has been happening::

  % git checkout -b my_0x sodium/cpp0x
  Branch my_0x set up to track remote branch refs/remotes/sodium/cpp0x.
  Switched to a new branch "my_0x"
  % git log
  commit c65edc0dce094b990b55955ed9dd1ede1885d360
  Author: bemandawes <bemandawes@b8fc166d-592f-0410-95f2-cb63ce0dd405>
  Date:   Sat Feb 21 13:31:16 2009 +0000
  
      Rebuild docs
      
      git-svn-id: http://svn.boost.org/svn/boost/branches/cpp0x@51363 b8fc166d-592f-0410-95f2-cb63ce0dd405
  
  commit 2605f00422d11957b9e1e305a8317cfb88e56d40
  Author: bemandawes <bemandawes@b8fc166d-592f-0410-95f2-cb63ce0dd405>
  Date:   Sat Feb 21 12:29:29 2009 +0000
  
      Both regular and 'all' tests passing
      
      git-svn-id: http://svn.boost.org/svn/boost/branches/cpp0x@51362 b8fc166d-592f-0410-95f2-cb63ce0dd405
  ...

Get files from another branch
-----------------------------

This one is dead easy.  You just check them out.  Say a couple of
files exist on branch *allmystuff*, but not on branch
*sentinel-iterator*.  For instance, you've got tons of things going on
*allmystuff* and now want to make the just sentinel iterator specific
stuff available to the world.  You make a branch of upstream svn::

  % git checkout -b sentinel-iterator svn/release
  % git checkout allmystuff libs/sentinel-iterator

At this point git status will show new files on your local branch.
