
How this was all set up
=======================

For historical interest.  This is a several-step and very
time-consuming process.  

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
