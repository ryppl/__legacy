
.. highlight:: git_shell

Development scenarios
=====================

Now we'll walk through several development scenarios and have a look
at the workflow.

.. _modularize_python:

"Modularize" an existing boost project
--------------------------------------

Let's "modularize" boost.python.  I check out ``ryppl``, which
currently hosts boost.python directly, not as a submodule (though by
the time you read this, python will be a submodule, so try out this
modularization on something else).

I'm in my fresh clone (without having done any ``git submodule init``
or any of that..  you may, but it isn't necessary.)


Import project into local repository
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

I cd into the python subdirectory and import its contents into a local
git repository::

  % cd libs/python 
  
  % git init
  Initialized empty Git repository in /tmp/src/libs/python/.git/
  
  % git add .
  
  % git commit -m "modularizing python"
  [master (root-commit) c16bad0] modularizing python
   680 files changed, 79509 insertions(+), 0 deletions(-)
   create mode 100644 CMakeLists.txt
   create mode 100644 build/Jamfile.v2
   create mode 100644 doc/Jamfile
   [etc]
   create mode 100644 todo.txt

You'll notice I've created a new git repository inside a git
repository... this kind of thing would confuse svn, but here it
doesn't matter; unlike subversion, git information exists only at the
root of each clone (in subversion ``.svn`` directories are sprinkled
through the entire checkout).

Push 
^^^^

Meanwhile I've created a repository to hold this project up on
gitorious.  I now push the code there::

  % git push git@gitorious.org:ryppl/python.git  <-- 'git@' is push url 
  Counting objects: 714, done.
  Delta compression using up to 8 threads.
  Compressing objects: 100% (708/708), done.
  Writing objects: 100% (714/714), 825.03 KiB, done.
  Total 714 (delta 127), reused 0 (delta 0)
  => Syncing Gitorious... [OK]
  To git@gitorious.org:ryppl/python.git
   + 1b112bc...c16bad0 HEAD -> master 

I've used the *push* url, since I have write access.

Clean the superproject
^^^^^^^^^^^^^^^^^^^^^^

Now that I have python's code safely pushed to a separate
publicly-visible repository, I can remove the python code from the
superproject.  I want to remove the directory ``libs/python``
entirely, as git will create ``libs/python`` itself when I add the
submodule::

  % cd ..               <-- move to directory libs/

  % rm -r python        <-- adios

  % git rm -r python    <-- stage the 'rm' for commit
  rm 'libs/python/CMakeLists.txt'
  rm 'libs/python/build/Jamfile.v2'
  rm 'libs/python/doc/Jamfile'
  ...

  % git commit -m "bye bye python"
  [master 2efae00] bye bye python
   680 files changed, 0 insertions(+), 79509 deletions(-)
   delete mode 100644 libs/python/CMakeLists.txt
   ...
   delete mode 100644 libs/python/todo.txt

For sanity let's verify that the working copy is clean::

  % git status
  # On branch master
  nothing to commit (working directory clean)

Add the submodule
^^^^^^^^^^^^^^^^^

Now add the git submodule to the superproject::

  % git submodule add git://gitorious.org/ryppl/python.git libs/python
  Initialized empty Git repository in /tmp/src/libs/python/.git/
  remote: Counting objects: 714, done.
  remote: Compressing objects: 100% (581/581), done.
  remote: Total 714 (delta 127), reused 714 (delta 127)
  Receiving objects: 100% (714/714), 825.03 KiB | 674 KiB/s, done.
  Resolving deltas: 100% (127/127), done.
  
.. note:: Notice I have used the ``git://`` url, not the ``git@`` url.
   	  The ``git://`` url is readonly and is the only type of URL
   	  that should be committed to the superproject.  The ``git@``
   	  urls are readwrite and authenticated via SSH.  I will soon
   	  use the latter to push commits from submodules, but I never
   	  commit them to superprojects.

Git has checked out the submodule for us.  If I check the status of
the superproject, I'll see::

  % git status
  # On branch master
  # Your branch is ahead of 'origin/master' by 1 commit.
  #
  # Changes to be committed:
  #   (use "git reset HEAD <file>..." to unstage)
  #
  #       modified:   .gitmodules
  #       new file:   libs/python
  #
  
And 'git diff --cached' shows me::

  % git diff --cached
  diff --git a/.gitmodules b/.gitmodules
  index a74cbf4..f6067c4 100644
  --- a/.gitmodules
  +++ b/.gitmodules
  @@ -10,3 +10,6 @@
   [submodule "libs/fiber"]
          path = libs/fiber
          url = git://gitorious.org/ripple/fiber.git
  +[submodule "libs/python"]
  +       path = libs/python
  +       url = git://gitorious.org/ryppl/python.git
  diff --git a/libs/python b/libs/python
  new file mode 160000                  <-- funny-looking mode
  index 0000000..c16bad0
  --- /dev/null
  +++ b/libs/python
  @@ -0,0 +1 @@
  +Subproject commit c16bad0e3f847375872e53bac319d2f724fbf569
  
Here we see a few lines added to .gitmodules as well as *new file mode
160000*...  this is a special mode that indicates you're committing as
a directory entry, not a file.  This is just how git does its
submodule bookkeeping.  The hash there records the commit at which the
submodule will be checked out.  This is the same special file that we
see in the line *new file: libs/python* of ``git status``.  The hash
is the same one that we see in the current output of ``git submodule
status``::

  % git submodule status
  -6d205b973e41c226eba838ef125d5a14f508e173 libs/chrono
  -413d393f7aaea99c85d8db7bd93e06b99465e84c libs/fiber
  -d0698203f19bf30518f58ce8058dca496dba8ecf libs/process
  -c16bad0e3f847375872e53bac319d2f724fbf569 libs/python
  -f1e2aa9ad7743beaf11296e4f7d6f960814a86b7 libs/wave
  
To finish up let's commit (and push)::

 % git commit -m "modularized python"
 [master 525e3b0] modularized python
  2 files changed, 4 insertions(+), 0 deletions(-)
  create mode 160000 libs/python

Recap
^^^^^

To modularize project **P** I have:

* Created a publicly-visible repository **PR** to hold the project I'm
  modularizing
* Imported **P** into a single git repo and pushed the results to
  **PR**.
* Deleted all trace of **P** from the superproject and committed
  the deletion.
* Added **PR** as a submodule to the superproject with directory
  ``libs/``\ **P**.
* Committed the addition to the superproject and pushed the results.

Now, looking at my submodule status::

   % git submodule status
   -6d205b973e41c226eba838ef125d5a14f508e173 libs/chrono
   -413d393f7aaea99c85d8db7bd93e06b99465e84c libs/fiber
   -d0698203f19bf30518f58ce8058dca496dba8ecf libs/process
   -c16bad0e3f847375872e53bac319d2f724fbf569 libs/python
   -f1e2aa9ad7743beaf11296e4f7d6f960814a86b7 libs/wave

I see the same thing as I did on initial checkout, with the addition
of one extra submodule (in this case python).  I get the workspace
ready for build with the same steps in first part of
:ref:`getting_started`:

* git submodule init
* git submodule update
* run cmake
* make genheaders
* ???
* profit


Start my own development branch of a library
--------------------------------------------

In :ref:`modularize_python` we modularized library ``boost.python``.

Say I have a lot of modifications to ``boost.python`` that I've been
working on.  Some of my clients are using my modifications, but
they're not yet in upstream boost, if they'll ever be.  I'm forced to
make in-house releases of boost-plus-my-new-python-features.  At the
same time, I want my code to be maximally available to the boost
community, as I hope to have my changes taken upstream, which would
both make a contribution to boost and simplify my job.

I'm going to need a public repository for my modifications to python.
On gitorious, I find the python repository at
``http://www.gitorious.org/ryppl/python``.

I'm logged in to gitorious, and have uploaded ssh keys as described in
:ref:`sshkeys`.  I click "clone this repository on gitorius" and am
taken to a page that says "Create a clone of *python* in *ryppl*".
I've chosen the default name, *straszheims-python*.

Back on my machine, I have a working clone of **ryppl** itself checked
out.  I've done the submodule ``init`` and ``update``.  My submodules
are::

  % cat .gitmodules 
  [submodule "libs/wave"]
          path = libs/wave
          url = git://gitorious.org/ryppl/wave.git
  [submodule "libs/chrono"]
          path = libs/chrono
          url = git://gitorious.org/ryppl/chrono.git
  [submodule "libs/process"]
          path = libs/process
          url = git://gitorious.org/ryppl/process.git
  [submodule "libs/fiber"]
          path = libs/fiber
          url = git://gitorious.org/ryppl/fiber.git
  [submodule "libs/python"]
          path = libs/python
          url = git://gitorious.org/ryppl/python.git

To change the url, I modify this file with a text editor, changing the
``python`` url to point to ``straszheims-python``::

  % cat .gitmodules 
  ... 
  [submodule "libs/python"]
          path = libs/python
          url = git://gitorious.org/ryppl/straszheims-python.git

And issue ``git submodule sync``::

  % git submodule sync
  Synchronizing submodule url for 'libs/chrono'
  Synchronizing submodule url for 'libs/fiber'
  Synchronizing submodule url for 'libs/process'
  Synchronizing submodule url for 'libs/python'
  Synchronizing submodule url for 'libs/wave'
  
Which will synchronize the submodules' git repos.  I can see that the
origin of the python project is now my clone by catting the
``.git/config`` file of the submodule::

  % cat libs/python/.git/config 
  [core]
          repositoryformatversion = 0
          filemode = true
          bare = false
          logallrefupdates = true
  [remote "origin"]
          fetch = +refs/heads/*:refs/remotes/origin/*
          url = git://gitorious.org/ryppl/straszheims-python.git   <-- mine
  [branch "master"]
          remote = origin
          merge = refs/heads/master
  
The next goal is to commit to the python submodule and make these
commits available.  Moving into the subproject's directory, I see::

  % cd libs/python   <-- I'm in subproject dir

  % git status
  # Not currently on any branch.   <-- hmm
  nothing to commit (working directory clean)
  
I need to be on a branch locally to commit anything.  I'll work on the
standard 'master' branch.  First I need to check it out::

  % git checkout master
  Switched to branch 'master' 

  % git status
  # On branch master
  nothing to commit (working directory clean)

Now I make my modifications in ``libs/python``, check them in, and
push them, again in the subproject's directory::

  % emacs             <-- make a bunch of changes..
  % git commit -m "Tons of stuff... this is my boost.python version 3 branch." 

And to make these changes public, I need to push them.  There's a
catch: the git URL that the python project was checked out from is
readonly.  To push, I add a remote called 'writable' that refers to
the same place (but the readwrite URL) and push there::

  % git remote add writable git@gitorious.org:ryppl/straszheims-python.git
  % git push writable
  Counting objects: 371, done.
  Delta compression using up to 8 threads.
  Compressing objects: 100% (219/219), done.
  Writing objects: 100% (223/223), 69.23 KiB, done.
  Total 223 (delta 155), reused 0 (delta 0)
  => Syncing Gitorious... [OK]
  To git@gitorious.org:ryppl/straszheims-python.git
     c16bad0..d57dd22  HEAD -> master
  
Moving back up to the superproject directory, ``git submodule`` shows
me that I've made a commit in various ways::

  % git submodule status
   6d205b973e41c226eba838ef125d5a14f508e173 libs/chrono (heads/master)
   413d393f7aaea99c85d8db7bd93e06b99465e84c libs/fiber (heads/master)
   d0698203f19bf30518f58ce8058dca496dba8ecf libs/process (heads/master)
  +d57dd2233e855b4dfb440c909df303c34f24d797 libs/python (heads/master)  <-- note the plus
   f1e2aa9ad7743beaf11296e4f7d6f960814a86b7 libs/wave (heads/master)
  
  % git submodule summary
  * libs/python c16bad0...d57dd22 (1):
    > Tons of stuff... this is my boost.python version 3 branch.

Regular git commands show me that things are modified as well.  ``Git
status`` for instance,::

  % git status                   
  # On branch master
  # Changed but not updated:
  #   (use "git add <file>..." to update what will be committed)
  #   (use "git checkout -- <file>..." to discard changes in working directory)
  #
  #       modified:   .gitmodules
  #       modified:   libs/python
  #
  
And ``git diff`` gives me the full monty:: 

  % git diff
  diff --git a/.gitmodules b/.gitmodules
  index 63fe174..9a9bf68 100644
  --- a/.gitmodules
  +++ b/.gitmodules
  @@ -12,4 +12,6 @@
          url = git://gitorious.org/ryppl/fiber.git
   [submodule "libs/python"]
          path = libs/python
  -       url = git://gitorious.org/ryppl/python.git
  +       url = git://gitorious.org/ryppl/straszheims-python.git   <-- changed url
  diff --git a/libs/python b/libs/python
  index c16bad0..d57dd22 160000
  --- a/libs/python
  +++ b/libs/python
  @@ -1 +1 @@
  -Subproject commit c16bad0e3f847375872e53bac319d2f724fbf569
  +Subproject commit d57dd2233e855b4dfb440c909df303c34f24d797     <-- new commit

I ``git add`` and commit::

  % git add .gitmodules libs/python <-- 'add' stages changes for commit

  % git commit -m "old hedgehog bones gutted from python and replaced with nutrient-rich chicken livers"
  [master bda6ca8] old hedgehog bones gutted from python and replaced with nutrient-rich chicken livers
   2 files changed, 4 insertions(+), 2 deletions(-)
  
Now, this gets me part of the way there: I have:

* my own branch of python with my changes on it
* local commits that update the superproject with my python goodies.

Others can try out my changes by simply switching to my python branch,
as I did to start development on the branch.  To make my changes
available to others, I can push my changes (of the superproject) to a
clone of the superproject::

  % git push git@gitorious.org:ryppl/straszheims-ryppl.git
  Counting objects: 7, done.
  Delta compression using up to 8 threads.
  Compressing objects: 100% (4/4), done.
  Writing objects: 100% (4/4), 455 bytes, done.
  Total 4 (delta 3), reused 0 (delta 0)
  => Syncing Gitorious... [OK]
  To git@gitorious.org:ryppl/straszheims-ryppl.git
     eaa3aca..bda6ca8  HEAD -> master
  
