   


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
  consumption.  I've chosen to name it "straszheim" for the
  purposes of this documentation.  This repository is now listed as a
  clone on the main boost page.

* Up comes a page showing the various urls for this clone.  

Clone your clone to your local machine
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Clone to your local machine via the 'push url' (there's a little
questionmark box there that shows you the command)::

  % git clone git@gitorious.org:~straszheim/boost/straszheim.git
  Initialized empty Git repository in /tmp/straszheim/.git/
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
          url = git@gitorious.org:~straszheim/boost/straszheim.git
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
  origin  git@gitorious.org:~straszheim/boost/straszheim.git
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
