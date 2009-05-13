.. highlight:: sh

Hacking Boost via Git
=====================

Getting started
---------------

Git clone the repository like this::

  git clone git://sodium.resophonic.com/boost

you should see this::

  Initialized empty Git repository in /home/troy/tmp/boost/.git/
  remote: Counting objects: 445342, done.
  remote: Compressing objects: 100% (124120/124120), done.
  remote: Total 445342 (delta 309283), reused 445335 (delta 309280)
  Receiving objects: 100% (445342/445342), 132.59 MiB | 11085 KiB/s, done.
  Resolving deltas: 100% (309283/309283), done.
  Checking out files: 100% (22868/22868), done.
  
and in the newly created directory boost/, you should be looking at a
checkout of the svn trunk::

  % git branch -l
  * trunk

  % ls
  BuildSlave.cmake  LICENSE_1_0.txt  boost.css      doc/        more/    tools/
  CMakeLists.txt    Welcome.txt      boost.png      index.htm   people/  wiki/
  INSTALL           boost/           bootstrap.bat  index.html  rst.css
  Jamroot           boost-build.jam  bootstrap.sh*  libs/       status/
  
Have a look at the branches::

  % git branch -a
  * trunk
  origin/BOOST_BUILD_PYTHON
  origin/BOOST_VERSION_NUMBER
  origin/Boost_Jam_994
  origin/CMake
  ... (etc)
  
there are tons of them (see below for how to be more selective).  The
important bits are the following:

origin/trunk
  corresponds to https://svn.boost.org/svn/boost/trunk

origin/release
  corresponds to https://svn.boost.org/svn/boost/branches/release.
  Actually everything in ``origin/\*`` corresponds to
  https://svn.boost.org/svn/boost/branches/\*, with the exception of
  'trunk' (above), and ``tags/*`` (below)

origin/tags/*
  Correspond to https://svn.boost.org/svn/boost/tags/release/*

There is no sandbox, see below for how to hack on sandbox code.

Commit some code
----------------

You can make local commits::

  % echo "hi" >> Welcome.txt 
  % git status
  # On branch trunk
  # Changed but not updated:
  #   (use "git add <file>..." to update what will be committed)
  #
  #       modified:   Welcome.txt
  #
  % git commit -a -m "test"
  Created commit afef0d0: test
   1 files changed, 1 insertions(+), 0 deletions(-)
  
and pull down changes to your local copies of remote branches, as
upstream changes arrive::

  % git pull
  remote: Counting objects: 3, done.
  remote: Compressing objects: 100% (2/2)remote: , done.
  remote: Total 2 (delta 1), reused 0 (delta 0)
  Unpacking objects: 100% (2/2), done.
  From git://sodium.resophonic.com/boost
     b550a06..8278aad  trunk      -> origin/trunk
  Removed BuildSlave.cmake
  Merge made by recursive.
   BuildSlave.cmake |   64 ------------------------------------------------------
   1 files changed, 0 insertions(+), 64 deletions(-)
   delete mode 100644 BuildSlave.cmake
  
Note, above, that the changes were pulled to 'origin/trunk', a remote
branch, not to 'trunk', your local branch based on it.  To merge new
remote trunk changes in to your local trunk changes, rebase::

  % git rebase origin/trunk
  First, rewinding head to replay your work on top of it...
  Applying test

To get someplace local to work that is based on, say, the release
branch::

  % git checkout -b my_release_branchname origin/release
  warning: You appear to be on a branch yet to be born.
  warning: Forcing checkout of origin/release.
  Checking out files: 100% (22207/22207), done.
  Branch my_release_branch set up to track remote branch refs/remotes/origin/release.
  Switched to a new branch "my_release_branch"

Now you can make modifications and commit to your branch::

  % echo "HI" >> INSTALL

  % git status
  # On branch my_release_branch
  # Changed but not updated:
  #   (use "git add <file>..." to update what will be committed)
  #
  #       modified:   INSTALL
  #

  % git commit -a -m "test commit"
  Created commit c41de88: test commit
  1 files changed, 1 insertions(+), 1 deletions(-)

and as new changes come in, you can fetch them::

  % git fetch
  remote: Counting objects: 3, done.
  remote: Compressing objects: 100% (2/2), done.
  remote: Total 2 (delta 1), reused 0 (delta 0)
  Unpacking objects: 100% (2/2), done.
  From git://sodium.resophonic.com/boost
     3e99925..0aa4644  release    -> origin/release
  
and again merge (rebase) your changes in to them, and all the other
goodness that git makes available::

  % git rebase origin/release
  First, rewinding head to replay your work on top of it...
  Applying test commit


Do some development
===================

Check out a branch to tweak on::  

  % git checkout -b gcc440releasefixes origin/release
  % git branch
  * gcc440releasefixes   # you're on this branch
    trunk

make some changes and commit to the local branch::

  emacs libs/serialization/src/xml_grammar.cpp
  git commit -a -m "Stop warnings from old use of spirit"

Now generate a patch, for applying back to svn, by diffing
the branch against the remote branch (which is synced to svn)::

  % git diff -p origin/release > /tmp/mypatch

it looks like this::

  % cat /tmp/mypatch
  diff --git a/libs/serialization/src/xml_grammar.cpp b/libs/serialization/src/xml_grammar.cpp
  index 4f2c37c..05904f4 100644
  --- a/libs/serialization/src/xml_grammar.cpp
  +++ b/libs/serialization/src/xml_grammar.cpp
  @@ -15,7 +15,7 @@
   #define BOOST_ARCHIVE_SOURCE
   #include <boost/archive/impl/basic_xml_grammar.hpp>
   
  -using namespace boost::spirit;
  +using namespace boost::spirit::classic;
 
   #include <boost/config.hpp>
 
Now to apply to svn.  Note that the patchfile above has leading paths
a/ and b/::

  % cd /path/to/svn/checkout
  % patch -p1 < /tmp/mypatch
  patching file libs/serialization/src/xml_grammar.cpp
  % svn commit -m "you have to retype the commit message"

Note that if the patch adds or removes files, svn won't be told it
should commit them::

  M      libs/units/test/CMakeLists.txt
  M      libs/regex/module.cmake
  !      tools/build/CMake/BoostBuildSlave.cmake
  !      tools/build/CMake/run_continuous_slave.py.in
  !      tools/build/CMake/post.py.in
  ?      CTestConfig.cmake

so you'll have to add/remove these by hand with ``svn add`` and ``svn
rm``, e.g.::

  % svn rm `svn status | grep ^! | awk '{ print $2 }'` 
  D         tools/build/CMake/BoostBuildSlave.cmake
  D         tools/build/CMake/run_continuous_slave.py.in
  D         tools/build/CMake/post.py.in
  % svn add `svn status | grep ^\? | awk '{ print $2 }'` 
  A         CTestConfig.cmake

Note that the process is a little lossy as various git commits become
one svn commit with a possibly different comment.  You can use 'git 
format-patch' to make a bunch of patch files containing commit messages,
like this::

  % git format-patch origin/release
  0001-.patch
  0002-.patch
  0003-.patch

  % cat 0001-.patch 
  From 559336b1b4666db55c2c78d3ee11fff47b552cf0 Mon Sep 17 00:00:00 2001
  From: troy <troy@zinc.dc.resophonic.com>
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

Having committed to svn, in a minute or so that commit will make its
way through svn to the main git mirror.  You're going to fetch the
updates down to your local clone (the examples no longer use the boost
mirror but a small testcase)::

  % git fetch
  remote: Counting objects: 5, done.
  remote: Compressing objects: 100% (2/2), done.
  remote: Total 3 (delta 1), reused 0 (delta 0)
  Unpacking objects: 100% (3/3), done.
  From /home/troy/gitting/git-repo1
    d7696b1..6c2a3d1  trunk      -> origin/trunk

but the changes will be only on your remote branch, not in your
working copy.  Since you're on a branch of origin/trunk, 'git pull'
will merge in the changes::

  % git pull
  Merge made by recursive

and git handles the merge just fine.  Surprisingly, it will even
handle the following situation: rename a local file 'foo' to 'bar',
modify and commit it.  Meanwhile, somebody modifies 'foo' and commits
to svn.  When you next fetch and pull, it will remember/detect that
your modified 'bar' started as 'foo', and merge upstream modifications
to 'foo' into your bar.  Looks like this::

  % git pull    
  Renamed foo => bar
  Auto-merged bar      # note: the upstream modifications are to foo
  Merge made by recursive.
   bar |    2 +-
   1 files changed, 1 insertions(+), 1 deletions(-)

Other things to try
===================

- make branches of the trunk and release and diff them, something rather 
  time consuming with subversion:
  
  SVN version::
  
    % svn diff http://svn.boost.org/svn/boost/branches/release http://svn.boost.org/svn/boost/trunk > svndiff
    svn: Caught signal
    svn: Error reading spooled REPORT request response
    [1]  + exit 1     svn diff http://svn.boost.org/svn/boost/branches/release  > svndiff
      
  GIT version::
  
    % git checkout -b local_trunk origin/trunk
    Branch local_trunk set up to track remote branch refs/remotes/origin/trunk.
    Switched to a new branch "local_trunk"

    % git diff local_trunk my_release_branch | wc -l
    250605

    % time git diff local_trunk my_release_branch >/dev/null
    git diff local_trunk my_release_branch > /dev/null  0.70s user 0.02s system 99% cpu 0.724 total

  250k Lines!
  
- Go to the cgit front end at http://sodium.resophonic.com/git/boost/,
  select 'release' from the top right pulldown, hit switch, type
  'beman' into the search box below it, choose 'log msg', hit search,
  and within an instant, see all commits mentioning beman on the
  release branch.  (Some won't mention Beman in the short message.
  Hit expand, and in the blink of an eye, see the full text.)

Various HOWTOS
==============

Track only certain branches
---------------------------

The main repository's branch namespace is badly polluted.  If you're
interested in, say, only ``trunk``, ``release``, and the latest
release tag, do::

  % mkdir -p boost/src
  % cd boost/src
  % git remote add -t trunk -t release -t tags/Boost_1_39_0 origin git://sodium.resophonic.com/boost

Nothing will get downloaded, but your git repository now has some
internal pointers to the upstream git mirror::

  % cat .git/config 
  cat .git/config 
  [core]
  	repositoryformatversion = 0
  	filemode = true
  	bare = false
  	logallrefupdates = true
  [remote "origin"]
  	url = git://sodium.resophonic.com/boost
  	fetch = +refs/heads/trunk:refs/remotes/origin/trunk
  	fetch = +refs/heads/release:refs/remotes/origin/release
  	fetch = +refs/heads/tags/Boost_1_39_0:refs/remotes/origin/tags/Boost_1_39_0

Then tell git to fetch the relevant code::

  % git fetch
  remote: Counting objects: 387996, done.
  remote: Compressing objects: 100% (119496/119496), done.
  Receiving objects: 100% (387996/387996), 123.74 MiB | 210 KiB/s, done.
  Resolving deltas: 100% (273366/273366), done.
  From git://sodium.resophonic.com/boost
   * [new branch]      trunk      -> origin/trunk
   * [new branch]      release    -> origin/release
   * [new branch]      tags/Boost_1_39_0 -> origin/tags/Boost_1_39_0
  
This will take a while, but the size of the repository will be
somewhat smaller than if you just clone the entire thing, and your
local branch namespace will be significantly less polluted:

  % git branch -a
    origin/release
    origin/tags/Boost_1_39_0
    origin/trunk

at this point nothing is checked out.  Check out a branch as usual and
have yourself a hack:

  % git checkout -b myfeature origin/release
  warning: You appear to be on a branch yet to be born.
  warning: Forcing checkout of origin/release.
  Checking out files: 100% (22185/22185), done.
  Branch myfeature set up to track remote branch refs/remotes/origin/release.
  Switched to a new branch "myfeature"

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

How this was all set up
=======================

This is a several-step process.  #1, git-svn clone the original
repository, to a private location (not where cgit can see it)::

  git svn clone http://svn.boost.org/svn/boost --no-checkout -Ttrunk -ttags/release -bbranches /path/to/boost_gitsvn

The only thing allowed to touch /path/to/boost-gitsvn is a cronjob.
Next create a bare repository someplace where cgit can see it (this is
what people will clone from)::

  mkdir /var/git/boost
  cd /var/git/boost
  git init --bare

Create your cronjob script, containing the following::

  cd /path/to/boost_gitsvn     
  git svn fetch                
  git push /var/git/boost 'refs/remotes/*:refs/heads/*' 2>&1 | grep -v 'Everything up-to-date'
  
which moves the gitsvn branches into the local namespace of the
/var/git/boost repository.  The ``grep -v`` keeps you from getting
email when there is nothing to do.  Note: thanks doener from
freenode:#git!

Now run that cronjob.  It should happily fetch and push.  Set that
script to run every so often.  I have:



Now, the /var/git/boost doesn't have a 'master'.  You can make 'trunk'
act like master like this::

  cd /var/git/boost
  git symbolic-ref HEAD resf/heads/trunk

Point your cgit at /var/git/boost (the
one getting pushed to, not the one doing the fetching).


