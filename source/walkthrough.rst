.. highlight:: git_shell

Walkthrough
-----------

Install git
^^^^^^^^^^^

Add details.

Install python
^^^^^^^^^^^^^^

Required modules are ``subprocess``, ``sys``, ``re``, ``os``, and
``optparse``.

Set up ryppl
^^^^^^^^^^^^

Clone the repository containing ryppl scripts::

  git clone git://gitorious.org/ryppl/bin ryppl-bins

in the directory ``ryppl-bins`` you will find an executable shell
script called ``git-ryppl``.  Put this on your path somewhere.

At this point you should be able to execute ``git ryppl version`` and
see something like ``Ryppl version 0.0a``.


Clone the ryppl superproject
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This is the rypplized boost

::

   git clone git://gitorious.org/ryppl/boost.git src

Now you've got an empty project with dirs :file:`cmake/` and
:file:`src/`.  File :file`.gitmodules` shows the mapping from local
directory to remote repository,::

  [submodule "src/accumulators"]
          path = src/accumulators
          url = git://gitorious.org/boost/accumulators.git
  [submodule "src/algorithm"]
          path = src/algorithm
          url = git://gitorious.org/boost/algorithm.git
  (etc)

And ``git submodule status`` shows that nothing has been checked out,

::

  -6dce83c277d48644fac187799876799eb66c97a2 cmake
  -0628a7a2d999bbbd62fd9877922c057f5f056114 src/accumulators
  -5cec8044c5408fadee71110194027b0e99b44721 src/algorithm
  ...

the leading minus sign says they're not checked out.  

Now execute ``git submodule init``, you'll see this::

  Submodule 'cmake' (git://gitorious.org/ryppl/cmake.git) registered for path 'cmake'
  Submodule 'src/accumulators' (git://gitorious.org/boost/accumulators.git) registered for path 'src/accumulators'
  Submodule 'src/algorithm' (git://gitorious.org/boost/algorithm.git) registered for path 'src/algorithm'
  ...
  
Now update the project locally with,::

  $ git submodule update
  Initialized empty Git repository in /root/fleh/src/cmake/.git/
  remote: Counting objects: 263, done.
  remote: Compressing objects: 100% (177/177), done.
  remote: Total 263 (delta 85), reused 232 (delta 66)
  Receiving objects: 100% (263/263), 566.58 KiB | 277 KiB/s, done.
  Resolving deltas: 100% (85/85), done.
  Submodule path 'cmake': checked out '6dce83c277d48644fac187799876799eb66c97a2'
  Initialized empty Git repository in /root/fleh/src/src/accumulators/.git/
  remote: Counting objects: 176, done.
  remote: Compressing objects: 100% (91/91), done.
  remote: Total 176 (delta 95), reused 154 (delta 82)
  Receiving objects: 100% (176/176), 154.93 KiB, done.
  Resolving deltas: 100% (95/95), done.
  Submodule path 'src/accumulators': checked out '0628a7a2d999bbbd62fd9877922c057f5f056114'
  ...
  Initialized empty Git repository in /root/fleh/src/src/xpressive/.git/
  remote: Counting objects: 277, done.
  remote: Compressing objects: 100% (178/178), done.
  remote: Total 277 (delta 109), reused 255 (delta 96)
  Receiving objects: 100% (277/277), 284.56 KiB | 294 KiB/s, done.
  Resolving deltas: 100% (109/109), done.
  Submodule path 'src/xpressive': checked out '64d71d9e873b4d0abbab2c9c089e3cefc960a706'
   
Now your checkout is populated with source, ready to build.

Scenario:  I want to work on a library
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We want to make modifications to project boost.python, with the
intention of eventually making a merge request to the project's owner.
This one is kind of longwinded and needs automation, I would think.

.. warning:: Do these steps in order!!!

.. rubric:: Clone the metaproject on gitorious

Make a clone of ryppl up on gitorious, using the "Clone this
repository on gitorious" link on `ryppl's gitorious page
<http://gitorious.org/ryppl/ryppl>`_.  Later this will contain a
modified submodule pointing to our clone of python, which we will
create later.  I have called mine *straszheims-ryppl*, here:
http://gitorious.org/~straszheim/ryppl/straszheims-ryppl

.. rubric:: Clone the project on gitorious

Using the same procedure as above, clone the python project.  The
clone button is on `this page <http://gitorious.org/boost/python>`_.

.. rubric:: Remove the old submodule

Remove these lines from :file:`.gitmodules`::

  [submodule "src/python"]
          path = src/python
          url = git://gitorious.org/boost/python.git
  
Add :file:`.gitmodules` to the pending commit::

  git add .gitmodules

Remove these lines from :file:`.git/config`::

  [submodule "src/python"]
          url = git://gitorious.org/boost/python.git
  
This is just for cleanliness, not part of the commit.

Remove the submodule from the cache::

  % git rm --cached src/python 
  rm 'src/python'

Git now shows that we're ready to delete it::

  $ git status
  # On branch 1.41.0
  # Your branch is ahead of 'origin/1.41.0' by 1 commit.
  #
  # Changes to be committed:
  #   (use "git reset HEAD <file>..." to unstage)
  #
  #       modified:   .gitmodules
  #       deleted:    src/python
  #
  # Modified submodules:
  #
  # * src/python 028025b...0000000 (5):
  #   < add some version numbers
  #
  # Untracked files:
  #   (use "git add <file>..." to include in what will be committed)
  #
  #       src/python/
  
Commit the change::

  % git commit -m "changing python submodule..."
  [1.41.0 489023d] changing python submodule...
   1 files changed, 0 insertions(+), 1 deletions(-)
   delete mode 160000 src/python
  
Now you've removed the old submodule.

.. rubric:: add the new submodule

First remove the untracked directory corresponding to the submodule::

  % rm -r src/python

Now add the new one::

  % git submodule add git://gitorious.org/boost/straszheims-python.git src/python
  Initialized empty Git repository in /home/troy/Projects/ryppl/tmp/boost2/src/python/.git/
  remote: Counting objects: 1191, done.
  remote: Compressing objects: 100% (768/768), done.
  remote: Total 1191 (delta 468), reused 1117 (delta 396)
  Receiving objects: 100% (1191/1191), 943.67 KiB | 590 KiB/s, done.
  Resolving deltas: 100% (468/468), done.

.. note:: Notice I have used the ``git://`` url, not the ``git@`` url.
   	  The ``git://`` url is readonly and is the only type of URL
   	  that should be committed to the superproject.  The ``git@``
   	  urls are readwrite and authenticated via SSH.  I will soon
   	  use the latter to push commits from submodules, but I never
   	  commit them to superprojects.

Now that the python repository now points to the right place::

  $ grep url src/python/.git/config 
          url = git://gitorious.org/boost/straszheims-python.git

Now git tells us that we've added the submodule, and shows the new
head commit::

  % git status
  # On branch 1.41.0
  # Your branch is ahead of 'origin/1.41.0' by 2 commits.
  #
  # Changes to be committed:
  #   (use "git reset HEAD <file>..." to unstage)
  #
  #       modified:   .gitmodules
  #       new file:   src/python
  #
  # Modified submodules:
  #
  # * src/python 0000000...8d3d698 (21):
  #   > that's basically it for overload resolution some upcoming numpy stuff mixed in :/
  #
  
And ``git diff --cached tells me``::

  diff --git a/.gitmodules b/.gitmodules
  index 30ccec5..64e4e98 100644
  --- a/.gitmodules
  +++ b/.gitmodules
  @@ -10,3 +10,6 @@
   [submodule "cmake"]
          path = cmake
          url = git://gitorious.org/ryppl/cmake.git
  +[submodule "src/python"]
  +       path = src/python
  +       url = git://gitorious.org/boost/straszheims-python.git
  diff --git a/src/python b/src/python
  new file mode 160000
  index 0000000..d6e0e56
  --- /dev/null
  +++ b/src/python
  @@ -0,0 +1 @@
  +Subproject commit d6e0e5699fcc241ff8470d5a35bbeb3946c1a0be
  
Wherein you can see that the new submodule has been added to
:file:`.gitmodules` and the exact commit of the submodule is somehow
associated (``file mode 160000``) with the path :file:`src/python`.

Commit the change::

  % git commit -m "add my python branch"
  [1.41.0 64d5917] add my python branch
   1 files changed, 1 insertions(+), 1 deletions(-)

Now you can push your changes to your ryppl branch.

Make and push modifications to your python project
""""""""""""""""""""""""""""""""""""""""""""""""""

Cd to project, modify a file, add to commit and commit::

  $ cd src/python
  $ echo "// modifications to python" >> include/boost/python.hpp 
  $ git add include/boost/python.hpp
  $ git commit -m "Dummy commit... demonstrating ryppl"

*Always* push your modifications to submodules before you commit the
modifications to the ryppl branch.  If you try to just push, git
complains::

  $ git push
  fatal: protocol error: expected sha/ref, got '
  ----------------------------------------------
  The git:// protocol is read-only.
  
  Please use the push url as listed on the repository page.
  ----------------------------------------------'
  
So add a remote that is writable.  I use the 'push' (``git@``) url and
name it *readwrite*::

  $ git remote add readwrite git@gitorious.org:boost/straszheims-python.git

And push::

  $ git push readwrite
  Counting objects: 9, done.
  Delta compression using up to 8 threads.
  Compressing objects: 100% (4/4), done.
  Writing objects: 100% (5/5), 453 bytes, done.
  Total 5 (delta 2), reused 0 (delta 0)
  => Syncing Gitorious... [OK]
  To git@gitorious.org:boost/straszheims-python.git
     8d3d698..d6e0e56  HEAD -> master

Now check your status up in the ryppl directory::

  $ git status
  # On branch 1.41.0
  # Your branch is ahead of 'origin/1.41.0' by 3 commits.
  #
  # Changed but not updated:
  #   (use "git add <file>..." to update what will be committed)
  #   (use "git checkout -- <file>..." to discard changes in working directory)
  #
  #       modified:   src/python
  #
  
You can just commit this, but let's check some stuff first.  ``git submodule status`` shows ::

  $ git submodule status
   6dce83c277d48644fac187799876799eb66c97a2 cmake (heads/master)
   0628a7a2d999bbbd62fd9877922c057f5f056114 src/accumulators (remotes/origin/1.41.0)
   5cec8044c5408fadee71110194027b0e99b44721 src/algorithm (remotes/origin/1.41.0)
   ...
   49b781309f926ea9a2bed09091fe276f32f7a92a src/core (remotes/origin/1.41.0)
  +8d3d698c598e1779f932e8a29e9131a23d55388e src/python  <-- plus
  
The plus means that the head of the currently checked out submodule
doesn't match what is in the index, and ``submodule summary`` shows::

  $ git submodule summary
* src/python 8d3d698...d6e0e56 (1):
  > Dummy commit... demonstrating ryppl

specifically what the new commits are.  Now you'd commit and push the
modifications to the superproject::

  $ git add src/python/
  $ git commit -m "update python"
  [1.41.0 709256c] update python
   1 files changed, 1 insertions(+), 1 deletions(-)
  % git push
  Counting objects: 18, done.
  Delta compression using up to 8 threads.
  Compressing objects: 100% (15/15), done.
  Writing objects: 100% (15/15), 1.19 KiB, done.
  Total 15 (delta 11), reused 0 (delta 0)
   
Now, you send email with your ryppl repository... when others check it
out and then ``submodule init`` and ``submodule update`` they get your
modifications to the python project.

Various howtos
--------------

Synchronize actual submodule clones to contents of :file:`gitmodules`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Commit modifications to :file:`.gitmodules`, rm the entry from
:file:`.git/config`, *rm the submodule directory from src/* then
``submodule init`` and ``submodule update``.  




