.. highlight:: git_shell

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

.. straszheim.process.tar.gz

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
  To git@gitorious.org:~straszheim/boost/straszheim.git
   * [new branch]      trunk_process_pub -> trunk_process
  => Syncing Gitorious... [OK]

So here, "origin" is as specified in the :file:`.git/config` file.  It
is where we originally cloned from: our sandbox.  The *refspec* is
simply ``frombranch:tobranch``, or from local branch
``trunk_process_pub`` to branch ``trunk_process`` on the remote.  Now
announce the availablility and location of the hacks.

You can browse the *trunk_process* branch at 
http://gitorious.org/~straszheim/boost/straszheim/commits/trunk_process

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
