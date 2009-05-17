.. highlight:: git_shell

Hacking Boost via Git
=====================

As of this writing (|today|) *there is no serious proposal to switch
primary source control for boost away from subversion to git* and this
document does not constitute such a proposal.

But it may become such a proposal.  This document intends to 

* establish what best practices would be
* provide a demonstration of the system 
* foment discontent

.. rubric:: Highly recommended reading:

Thanks to the folks on freenode's #git:

* `Git from the bottom up <http://ftp.newartisans.com/pub/git.from.bottom.up.pdf>`_ (See also the links at the end of this document).
* `Git for Computer Scientists <http://eagain.net/articles/git-for-computer-scientists/>`_
* `Git home page <http://git-scm.com>`_

Getting started
---------------

Register and make a clone on gitorious
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Go to http://gitorious.org and register.  You'll need to upload an
  ssh key for committing purposes.

* Go to this page: http://gitorious.org/boost, have a quick look.
  That's the main project page.

* Click on the 'svn' link to take you to
  http://gitorious.org/boost/svn.  This is the git repository that is
  tracking subversion (as is http://sodium.resophonic.com/git/boost).

* Find the link on the right that says "Clone this repository on
  Gitorious".  This is where you will push your code to for public
  consumption.  I've chosen to name it "straszheim-sandbox" for the
  purposes of this documentation.  This repository is now listed as a
  clone on the main boost page.

* Up comes a page showing the various urls for this clone.  

Clone your clone to your local machine
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Clone to your local machine via the 'push url' (there's a little
questionmark box there that shows you the command)::

  % git clone git@gitorious.org:~straszheim/boost/straszheim-sandbox.git
  Initialized empty Git repository in /tmp/straszheim-sandbox/.git/
  remote: Counting objects: 389544, done.
  remote: Compressing objects: 100% (123052/123052), done.
  remote: Total 389544 (delta 269483), reused 383698 (delta 263651)
  Receiving objects: 100% (389544/389544), 117.18 MiB | 225 KiB/s, done.
  Resolving deltas: 100% (269483/269483), done.
  Checking out files: 100% (22939/22939), done.

Don't be confused by the fact that you're pulling from the push url.
The semantics are that the "public" (``git://...``) and http clone
urls are readonly.  The "push" (``git@gitorious...``) url is
readwrite.  You should now be looking at a checkout of the svn trunk::

  % ls
  CMakeLists.txt     LICENSE_1_0.txt  boost.css      doc/        more/    tools/
  CTestConfig.cmake  Welcome.txt      boost.png      index.htm   people/  wiki/
  INSTALL            boost/           bootstrap.bat  index.html  rst.css
  Jamroot            boost-build.jam  bootstrap.sh*  libs/       status/

You may inspect the file :file:`.git/config` in the checked out
directory,

.. code-block:: cfg

  [core]
          repositoryformatversion = 0
          filemode = true
          bare = false
          logallrefupdates = true
  [remote "origin"]
          url = git@gitorious.org:~straszheim/boost/straszheim-sandbox.git
          fetch = +refs/heads/*:refs/remotes/origin/*
  [branch "master"]
      remote = origin
      merge = refs/heads/master

note that the local identifier ``origin`` is associated with our
push url, which is *remote* and that there is a "refspec" listed
under ``fetch``.  You may have multiple remotes.  There is one local
branch, *master*, which is associated with branch *master* of the
remote called *origin*.

Your *master* branch is already checked out.  Have a look at your
branches::

  % git branch -a
  * master
    origin/HEAD
    origin/master
    origin/release

the asterisk indicates the branch that is currently checked out.
This *master* branch is associated with the svn *trunk*.  Some
number of release tags are also available::

  % git tag -l
  Boost_1_38_0
  Boost_1_39_0

Add a remote for svn 
^^^^^^^^^^^^^^^^^^^^

The magic of git starts when accessing multiple repositories.  The
standard development cycle will be,

#. Make a local branch for your project

#. Write code, commit to the local branch.

#. Rebase your local branch against changes coming in to the master
   (svn)

#. Merge your project to a publicly visible branch

#. Push that branch back up to gitorious and announce its availability.

#. (optional) Format and apply patches to svn.  Git makes this
   really easy.  

So we'll need access to the remote 'svn' git repository, where code
from svn arrives.  Add a remote for svn, using the readonly "public"
url::

  % git remote add svn git://gitorious.org/boost/svn.git

You can have a look at them::

  % git remote -v
  origin  git@gitorious.org:~straszheim/boost/straszheim-sandbox.git
  svn     git://gitorious.org/boost/svn.git
  
Also notice that the following lines have appeared in your
:file:`.git/config`

.. code-block:: cfg

   [remote "svn"]
         url = git://gitorious.org/boost/svn.git
         fetch = +refs/heads/*:refs/remotes/svn/*
  
The *fetch* line above has a *refspec* on the right hand side.  This
one essentially means 'fetch all branches'.  If you run ``git branch
-a`` at this point you won't see the remote svn branches.  Go ahead and 
fetch any updates from svn::

  % git fetch svn
  remote: Counting objects: 139, done.
  remote: Compressing objects: 100% (74/74), done.
  remote: Total 74 (delta 64), reused 0 (delta 0)
  Unpacking objects: 100% (74/74), done.
  From git://gitorious.org/boost/svn
   * [new branch]      master     -> svn/master
   * [new branch]      release    -> svn/release

You'll note that this one ran very quickly; this is because nothing
new has arrived in svn since you cloned from it.  Now you'll have
remote branches pointing to svn::

  % git branch -a
  * master
    origin/HEAD
    origin/master
    origin/release
    svn/master
    svn/release
 
.. note:: Currently only the trunk and release branches are mirrored
   	  on gitorious, for reasons of namespace hygiene.  The
   	  repository at http://sodium.resophonic.com/git/boost has
   	  many more branches.  You also always have the option of
   	  ``svn export``\ -ing into a git branch.

.. _featurebranch:

Do some development
-------------------

Make a local "feature" branch
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Now we'll make a local branch to commit to as we develop some feature.
For the purposes of this exercise, I'll make a branch of the boost
trunk, with the addition of the 'process' library from the vault.

The recommended workflow here is to 'rebase' my private branch on top
of changes to the trunk as they come in, and then when I'm ready to
release some code, to merge and push on a separate branch.  Rebase is
a great tool, but one must use it with care.  I'll choose a naming
scheme for my branches here that helps remember how things should be
done.

.. warning:: Rebase vs Merge

   Note and follow the naming scheme here, it will help you keep your
   rebases and merges straight.

   Rebase can be "dangerous" in subtle ways: *Never rebase branches or
   trees that you pulled.  Only rebase local branches*.  See the
   following links for full discussion:

   http://blog.experimentalworks.net/2009/03/merge-vs-rebase-a-deep-dive-into-the-mysteries-of-revision-control/

   http://gitguru.com/2009/02/03/rebase-v-merge-in-git/

   http://stackoverflow.com/questions/457927/git-workflow-and-rebase-vs-merge-questions

   http://lwn.net/Articles/328436/

Make a local branch from the trunk.  Name it *trunk_process_priv*,
meaning "based on the trunk, plus process, private".  The private bit
is important: you're not going to push this::

  % git checkout -b trunk_process_priv
  Switched to a new branch "trunk_process_priv"

Git branch shows you where you are::

  % git branch
  master
  * trunk_process_priv

Hack hack
^^^^^^^^^

I unpack the process code and copy it into the source tree.  At this
point git hasn't added it to the pending commit::

  % git status
  # On branch trunk_process_priv
  # Untracked files:
  #   (use "git add <file>..." to include in what will be committed)
  #
  #       boost/process.hpp
  #       boost/process/
  #       libs/process/
  
I add the new files to the commit::

  % git add boost/process.hpp boost/process/ libs/process/
  % git status
  # On branch trunk_process_priv
  # Changes to be committed:
  #   (use "git reset HEAD <file>..." to unstage)
  #
  #       new file:   boost/process.hpp
  #       new file:   boost/process/child.hpp
  #       new file:   boost/process/config.hpp
  (etc)

and *fire*::

  % git commit -m "Process from the vault"
  Created commit 013e5ac: Process from the vault
  101 files changed, 10048 insertions(+), 0 deletions(-)
  create mode 100644 boost/process.hpp
  create mode 100644 boost/process/child.hpp
 
Redo a bad commit
^^^^^^^^^^^^^^^^^

I have a look at the git log::

  % git log
  commit 013e5ac89aa9298a8bb98d75fa1f1666340b2d77
  Author: troy <troy@zinc.(none)>
  Date:   Sun May 17 12:52:00 2009 -0400
  
      Process from the vault
  
And realize that I didn't set my email address correctly.  I can undo
the commit (!)::

  % git reset --soft HEAD^

which is safe because I haven't pushed the bad commit anywhere.  The
``--soft`` argument leaves the tree and index untouched (my
``boost::process`` files go back to being "Changes to be
committed"). ``HEAD`` is the current head, and the carat means ``minus
one``, so that just all just means "undo the last commit".  Now I set
my email address::

  % git config --global user.name "troy d. straszheim"
  % git config --global user.email "troy@resophonic.com"

and recommit::

  % git commit -m "Process from the vault"
  (same output as before)
  % git log
  commit 3b118595c053509810c6ea0256d67dd92b796e3b
  Author: troy d. straszheim <troy@resophonic.com>
  Date:   Sun May 17 14:03:38 2009 -0400

      Process from the vault

  commit 26a0f19b5d21d86292fe4bcccb8fa2f3212a052d
  Author: danieljames <danieljames@b8fc166d-592f-0410-95f2-cb63ce0dd405>
  Date:   Sat May 16 14:58:33 2009 +0000

      Merge dynamic bitset from release.
    
  (etc)

So note that our commit comes after danieljames' 26a0f19....

.. straszheim-sandbox.process.tar.gz

Rebase
^^^^^^

Assume that some time has gone by and new changes have come into the
trunk that I need.  I'll fetch down the new changes from svn.  This
won't change my working tree; it will just put them on my "remote
branch"::

  % git fetch svn
  remote: Counting objects: 25, done.
  remote: Compressing objects: 100% (13/13), done.
  remote: Total 13 (delta 12), reused 0 (delta 0)
  Unpacking objects: 100% (13/13), done.
  From git://gitorious.org/boost/svn
     6feea60..7b88c98  master     -> svn/master
  
Ah, there are some new changes there.  Now I want to "re-base" my
local changes on top of them.  This isn't a merge: I'm going to take
the changes that I've made since the last time I fetched from svn, and
make patches out of them, then I'm going to apply them to the new svn
head.  See the links in :ref:`featurebranch`, for a full discussion. ::


  % git rebase svn/master
  First, rewinding head to replay your work on top of it...
  Applying Process from the vault
  
and looking again at the git log::

  commit d6a58a60a2f26f708fcd0e928ea3dda825fe4b8b
  Author: troy d. straszheim <troy@resophonic.com>
  Date:   Sun May 17 14:03:38 2009 -0400

      Process from the vault

  commit 7b88c980838ab57efc7eddd42ac11e912952c98a
  Author: bemandawes <bemandawes@b8fc166d-592f-0410-95f2-cb63ce0dd405>
  Date:   Sun May 17 15:55:46 2009 +0000
  
      Fix Filesystem #2925, copy_file atomiticity
      
      git-svn-id: http://svn.boost.org/svn/boost/trunk@53073 b8fc166d-592f-0410-95
  
  (... more commits ...)

  commit 26a0f19b5d21d86292fe4bcccb8fa2f3212a052d
  Author: danieljames <danieljames@b8fc166d-592f-0410-95f2-cb63ce0dd405>
  Date:   Sat May 16 14:58:33 2009 +0000

      Merge dynamic bitset from release.
    
  (etc)

So what has happened here is that our commit has been reapplied,
*rebased* on the new svn trunk.  **NOTE THAT THE COMMIT HASH HAS
CHANGED**.  If we had pushed this branch, and somebody had pulled it,
then there is the opportunity for nasty merge conflicts later on.  So
we don't push it.

Push out our code
^^^^^^^^^^^^^^^^^

In order to make this patch available, we'll push a *merged* version.
First we make the branch that we're going to push.  In this case I'll
give it a name ending in *_pub* to indicate that no rebasing should
happen on this branch.  We want the branch to be based on the svn
trunk::

  % git checkout -b trunk_process_pub svn/master

have a peek at the last three commits, they are as expected::

  % git log -n2 --pretty=oneline
  7b88c980838ab57efc7eddd42ac11e912952c98a Fix Filesystem #2925, copy_file atomiticity
  6feea60c25b3fac8b4e2878a5834d6f49379fecf Allow the Boost.Test library to be built with Sun CC

and *merge* in our changes from the private branch::

  % git merge trunk_process_priv
  Updating 7b88c98..d6a58a6
  Fast forward
  boost/process.hpp                                  |   50 ++
  boost/process/child.hpp                            |  200 +++++++
  boost/process/config.hpp                           |   41 ++
  boost/process/context.hpp                          |  209 +++++++
  boost/process/detail/file_handle.hpp               |  406 ++++++++++++++
  ...

now we see process tacked on to the end::

  % git log -n3 --pretty=oneline
  d6a58a60a2f26f708fcd0e928ea3dda825fe4b8b Process from the vault
  7b88c980838ab57efc7eddd42ac11e912952c98a Fix Filesystem #2925, copy_file atomiticity
  6feea60c25b3fac8b4e2878a5834d6f49379fecf Allow the Boost.Test library to be built with Sun CC

and we push this branch up to our git clone at gitorious::

  % git push origin trunk_process_pub:trunk_process
  Counting objects: 237, done.
  Compressing objects: 100% (191/191), done.
  Writing objects: 100% (192/192), 124.68 KiB, done.
  Total 192 (delta 117), reused 0 (delta 0)
  To git@gitorious.org:~straszheim/boost/straszheim-sandbox.git
   * [new branch]      trunk_process_pub -> trunk_process
  => Syncing Gitorious... [OK]

So here, "origin" is as specified in the :file:`.git/config` file.  It
is where we originally cloned from: our sandbox.  The *refspec* is
simply ``frombranch:tobranch``, or from local branch
``trunk_process_pub`` to branch ``trunk_process`` on the remote.  Now
announce the availablility and location of the hacks.

You can browse the *trunk_process* branch at 
http://gitorious.org/~straszheim/boost/straszheim-sandbox/commits/trunk_process

Lather, rinse, repeat
^^^^^^^^^^^^^^^^^^^^^

So the general process is:

* Branch from ``svn/master`` (svn trunk) to some_feature_priv
* Commit to the priv branch 
* Periodically fetch and rebase
* Switch to some_feature_pub and merge from some_feature_priv
* Push *some_feature_pub* to a public *some_feature*

One thing to pay attention to is what you're rebasing on.  If we want
to do this development cycle again, the second time we will need to
rebase on our public branch, **not** on *svn/master*.

Let's iterate again.  I switch to my private development branch::

  % git checkout trunk_process_priv
  Switched to branch "trunk_process_priv"
  Your branch is ahead of the tracked remote branch 'svn/master' by 1 commit.

make some minor tweaks and commit::

  % git status
  # On branch trunk_process_priv
  # Changed but not updated:
  #   (use "git add <file>..." to update what will be committed)
  #
  #       modified:   boost/process.hpp
  #
  no changes added to commit (use "git add" and/or "git commit -a")
  % git commit -a -m "Minor tweak to process header"
  Created commit d8b9f1c: Minor tweak to process header
   1 files changed, 2 insertions(+), 2 deletions(-)
  
pull down the latest bits from svn::

  % git fetch svn
  remote: Counting objects: 11, done.
  remote: Compressing objects: 100% (6/6), done.
  remote: Total 6 (delta 5), reused 0 (delta 0)
  Unpacking objects: 100% (6/6), done.
  From git://gitorious.org/boost/svn
     7b88c98..4a25821  master     -> svn/master
  
and (here's the different bit), I merge upstream changes into my
public branch::

  % git co trunk_process_pub
  % git pull svn master

Then rebase my private branch on the public::

  % git co trunk_process_priv     
  % git rebase trunk_process_pub
  First, rewinding head to replay your work on top of it...
  Applying Process from the vault
  Applying Minor tweak to process header
  
and have a look at my rebased private development branch::

  commit 1cecb3a99a15208aad3c2a6c4d5d21ce9e683f54
  Author: troy d. straszheim <troy@resophonic.com>
  Date:   Sun May 17 14:43:38 2009 -0400
  
      Minor tweak to process header
  
  commit 2f85eeacae47b2b8f29ec9d682b16f7011dcbd59
  Author: troy d. straszheim <troy@resophonic.com>
  Date:   Sun May 17 14:03:38 2009 -0400
  
      Process from the vault
  
  commit 4a258213274e1d09bff7cac3f602d6b275ba8144
  Author: bemandawes <bemandawes@b8fc166d-592f-0410-95f2-cb63ce0dd405>
  Date:   Sun May 17 18:13:06 2009 +0000
  
      fix doc example typo
      
      git-svn-id: http://svn.boost.org/svn/boost/trunk@53074 b8fc166d-592f-0410-95f2-cb63ce0dd405
  
  commit 7b88c980838ab57efc7eddd42ac11e912952c98a
  Author: bemandawes <bemandawes@b8fc166d-592f-0410-95f2-cb63ce0dd405>
  Date:   Sun May 17 15:55:46 2009 +0000
  
      Fix Filesystem #2925, copy_file atomiticity
      
      git-svn-id: http://svn.boost.org/svn/boost/trunk@53073 b8fc166d-592f-0410-95f2-cb63ce0dd405
  
again the commits are nicely lined up atop the latest bits from the
trunk.  Switch to the pub branch, merge and push::

  % git checkout trunk_process_pub  
  Switched to branch "trunk_process_pub"
  Your branch and the tracked remote branch 'svn/master' have diverged,
  and respectively have 1 and 1 different commit(s) each.
  % git merge trunk_process_priv
  
  % git push origin trunk_process_pub:trunk_process

Submitting back to subversion
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

it looks like this::

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
  % git init
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
  warning: no common commits
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

at this point nothing is checked out::

  % git branch -l
  (no output)

So check out a branch and have yourself a hack.  In this case to
maintain the proposed Boost.Process library against the relesae
branch.  We're calling it *feature*\ ``_priv`` for reasons explained in
:ref:`rebase_vs_merge` ::

  % git checkout -b release_plus_process_priv origin/release
  warning: You appear to be on a branch yet to be born.
  warning: Forcing checkout of origin/release.
  Checking out files: 100% (22185/22185), done.
  Branch release_plus_process_priv set up to track remote branch refs/remotes/origin/release.
  Switched to a new branch "release_plus_process_priv"

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

This is a several-step and very time-consuming process.  I have plans
to modify this to push to a repository on `gitorious.org <http://gitorious.org>`_

* git-svn clone the original repository, to a private location (not
  where cgit can see it)::

    % git svn clone http://svn.boost.org/svn/boost --no-checkout -Ttrunk -ttags/release -bbranches /path/to/boost_gitsvn

  The only thing allowed to touch /path/to/boost-gitsvn is a cronjob.
  Nobody pushes to this repository.

* Next create a bare repository someplace where cgit can see it (this
  is what people will clone from)::

    % mkdir /var/git/boost
    % cd /var/git/boost
    % git init --bare

* Create your cronjob script, containing the following::

    % cd /path/to/boost_gitsvn     
    % git svn fetch                
    % git push /var/git/boost 'refs/remotes/*:refs/heads/*' 2>&1 | grep -v 'Everything up-to-date'
    % git push gitorious refs/remotes/trunk:refs/heads/master
    # and so on for other branches mirrored to gitorious

  which moves the gitsvn branches into the local namespace of the
  /var/git/boost repository.  The ``grep -v`` keeps you from getting
  email when there is nothing to do.  Note: thanks doener from
  freenode:#git!

* Now run that cronjob.  It should happily fetch and push.  Set that
  script to run every so often. 

* Now, the repository that you're pushing svn commits to,
  ``/var/git/boost``, doesn't have a 'master'.  This will give the
  uninitiated a confusing error when cloning the repository.  Solve
  the problem by making 'trunk' act like master like this::

    % cd /var/git/boost
    % git symbolic-ref HEAD refs/heads/trunk

* Point your cgit at /var/git/boost (the one getting pushed to, not
  the one doing the fetching).


.. rubric:: Footnotes

.. [#quickpatch] A quicker way, if you keep a clean subversion
   		 checkout laying around in :file:`/tmp/svn`:
   		 ``git diff origin/release | (cd /tmp/svn ;
   		 patch -p1)``

