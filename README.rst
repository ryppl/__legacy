.. title:: Ryppl - Git-based Software Development / Testing / Installation


================================================================
A Git-based Software Development / Testing / Installation System
================================================================

.. image:: http://www.ryppl.org/_static/ryppl.png
   :align: right

-----------
About Ryppl
-----------

Think of Ryppl as a `Git <http://git-scm.com>`_-based `package
management <http://en.wikipedia.org/wiki/Package_management_system>`_
and testing system designed to accomodate both end-users *and*
developers.  Unlike a traditional package manager, which delivers
binaries and/or a source snapshot, when ryppl downloads a package, it
gives you a clone of a Git repository, with that package's entire
development history.

--------------------
Support This Project
--------------------

Most contributors are giving their time to this project for free.  If
you make a donation to Ryppl, it will be used to pay for the time of
those who can't afford to be quite so generous.  We need their help,
and they need to pay the bills, so please consider `making a donation
<http://pledgie.com/campaigns/9508>`_.  Thanks!

-------------
Documentation
-------------

User Documentation
::::::::::::::::::

For emergent user-level HTML documentation, see http://www.ryppl.org

Developer Documentation
:::::::::::::::::::::::

This rest of this document is a getting-started guide for Ryppl
developers - the people who will be checking out from this repository
and are working on development of the ryppl project.  

...............
Things To Learn
...............

* First, get a handle on `the technologies
  <http://www.ryppl.org/technology.html>`_ we're using.

* Then, take a look at `The Hitchhiker's Guide to Packaging
  <http://guide.python-distribute.org/>`_, which describes some of the
  Python packaging and distribution tools we're exploiting.  You can
  find Git mirrors of the essential codebases `at Github
  <http://github.com/ryppl>`_.

Ryppl itself is, at the moment, a thin layer over distutils2_ and 
`our fork`_ of pip_. [#upstream]_  Ryppl reads 
distutils2 project metadata from the ``.ryppl`` folder and and feeds
it to ``setuptools.setup``.  If you don't see many changes in this
project yet, it's because we spent a good man-month or more getting
windows portability into pip_ (see `our fork`_).

.. _pip: http://pip.openplans.org

.. _distutils2: http://tarekziade.wordpress.com/2010/04/08/a-small-distutils2-foretaste/

.. _our fork: http://github.com/ryppl/pip

.................
Running The Tests
.................

One of the first things you'll want to do as a developer is get
something running, and have a framework that will tell you if you
broke something.

Testing Prerequisites
=====================

1. **Install** Git_.  On Windows, this means MSysGit_.  We will
   probably eliminate this requirement one day by using Dulwich_, so
   end-users don't have to install Git.

.. Note:: If you are going to use MSysGit on Windows and plan to use Git from
   Windows command prompt (cmd.exe) as opposed to the bash shell, here are some
   tricks to make your life easier.
   
   1. The MSysGit installer will give you three options for how you would like
      to configure Git's environment. The default is (a) to run Git from bash.
      The other two are (b) to put "git" in the Windows PATH, and (c) to put
      "git" and all the other Unix utilities in the Windows PATH. You should
      pick (b), the option called "Run Git from the Windows Command Prompt".
   
   2. When the MSysGit installer asks you how you would like Git to handle
      newlines on checkout and commit, select the option that says, "Check out
      as-is, commit as-is". That tells git to not mess with the line endings.
      You are encouraged to not check in files with crlf line endings, however.
      *TODO: is this the behavior we want?*

   3. You can use notepad.exe as Git's text editor for things like commit
      messages and the like, but you need to fix up the newline characters
      first. Create a file ``notepad.cmd`` alongside ``git.cmd`` in your
      ``C:\Program Files\Git\cmd`` directory. It should contain the following::
      
         @setlocal
         @set COMMIT_EDITMSG=%1
         @set COMMIT_EDITMSG=%COMMIT_EDITMSG:/=\%
         @del /q %COMMIT_EDITMSG%.tmp 2>1 1>nul
         @for /f "tokens=*" %%i in (%COMMIT_EDITMSG%) do @echo %%i >>%COMMIT_EDITMSG%.tmp
         @move /y %COMMIT_EDITMSG%.tmp %COMMIT_EDITMSG% 2>1 1>nul
         @notepad %COMMIT_EDITMSG%
         @endlocal

      Then execute the following command::

         > git config --global core.editor notepad.cmd
    
   4. You need to disable the pager used internally by git. As of the time of
      this writing (2010-7-2), MSysGit ships with a buggy version of
      less.exe that will cause some git commands to hang or crash cmd.exe.
      You can turn git's internal use of less.exe with the following::
      
      > git config --global core.pager cat
      
   5. There is a bug in how git handles various ``git help`` commands that
      causes the external browser to fail to display the requested help topic.
      You can work around the problem by going into the
      ``C:\Program Files\Git\doc\git\html`` directory and copying all
      ``git-*.html`` files to ``git*.html`` files (i.e., strip the hyphen
      after ``git`` in the filename).
    
2. **Git submodules** need to be initialized and updated.  From the
   root of your ryppl source tree, ::

     % git submodule init
     % git submodule update

3. **Install** virtualenv_.  You need version 1.4.0 or greater. Get it from your
   OS package manager (usually listed as ``python-virtualenv`` or
   ``py-virtualenv``) if you can, and skip to `step 6`__.  Otherwise, use
   setuptools as detailed below

   __ prerequisites-done_
   .. _install-setuptools:

      .. comment   

4. **Install setuptools** (the ``easy_install`` program for installing
   Python packages) if you don't already have it.  Your package
   manager may have it (e.g. as ``py-setuptools``), or you may be able
   to get a prebuilt package from `PyPi
   <http://pypi.python.org/pypi/setuptools>`_, but the most universal
   way is to `download ez_setup.py
   <http://peak.telecommunity.com/dist/ez_setup.py>`_ and run it with
   Python::

     % python ez_setup.py

   On windows, ``easy_install``\ ed executables don't go in your
   ``PATH`` by default, so you'll need to add something like
   ``c:\Python26\Scripts`` to your path, or just spell the full path
   to the executables, to make the rest of this work.

5. **Use setuptools** to get |virtualenv|_::

     % easy_install virtualenv

5. **Use setuptools** to get |scripttest|_::

     % easy_install scripttest

   .. _prerequisites-done:

      .. comment   

6. There is **no step 6**.  You're done!

.. _virtualenv: http://pypi.python.org/pypi/virtualenv
.. _scripttest: http://pythonpaste.org/scripttest
.. _Dulwich: https://launchpad.net/dulwich

Fully Automated Testing
=======================

The easiest way to run the tests is to invoke the ``self_test.py``
script in the ``test/`` subdirectory.  It sets up a virtual python
installation (using |virtualenv|_), installs all necessary
prerequisites there, and then launches the tests.  Any command-line
arguments are passed on to |nosetests|_ (but read on for two
exceptions).  This is the approach that will be used by BuildBots.

.. |virtualenv| replace:: `virtualenv`
.. |scripttest| replace:: `scripttest`
.. |nosetests| replace:: `nosetests`
.. _nosetests: nose_
.. _nose: http://somethingaboutorange.com/mrl/projects/nose

Testing For Local Development
=============================

To speed up the edit/test/debug cycle, you can ask ``self_test.py`` to
create the testing environment once and then print out the command you
can use repeatedly to run the tests:

.. parsed-literal::

  % self_test.py --prepare-env=\ *some-path*

which will prepare a testing environment in *some-path*, and print out
a |nosetests|_ command that runs the tests.  Please consult the nose_
documentation for information about additional options you might want
to pass.  Two likely candidates are ``-v`` and ``-x``.

Using Distribute_ Instead of Setuptools
=======================================

.. _Distribute: http://pypi.python.org/pypi/distribute

The only other argument recognized by ``self_test.py`` itself (and not
passed on to nose_) is ``--distribute``, which will cause the testing
environment to be prepared with Distribute_ rather than setuptools.
This option should be considered experimental, at least until we have
more information on `this issue
<http://bitbucket.org/tarek/distribute/issue/164/>`_.

.................
Building The Docs
.................

.. Note:: right now you can't get a complete build of the docs under
   Cygwin_ because there's no GraphViz_ binary in the Cygwin repo, and
   building GraphViz_ under Cygwin hangs at some point.  Cygwin users
   can use a `native Win32 installation
   <http://graphviz.org/Download_windows.php>`_ of GraphViz, but it
   will warn you that it can't generate the image because make will be
   passing it a Cygwin-style path.  That's ok if you just care about
   the HTML parts.  Otherwise, just use the windows-native tools as
   described below.

   A front-end path-converting wrapper might work here if someone is
   really committed to getting a *complete* doc build under Cygwin.

.. _Cygwin: http://cygwin.com
.. _GraphViz: http://graphviz.org

Setting up prerequisites
========================

1. **Get Python 2.x**.  If your OS doesn't have a builtin package
   manager that can install Python for you, get it from `Python.org
   <http://python.org/download/>`_.

2. **Install Sphinx**.  Get it from your OS package manager (usually
   listed as ``python-sphinx`` or ``py-sphinx``) if you can, and skip
   to step 5.  Otherwise, use setuptools as detailed below

3. **Install setuptools** (see `this step <#install-setuptools>`_).

4. **Use setuptools to get Sphinx**.  The servers were really slow
   last time I checked; expect this to take a while (add ``-v`` if
   you're easily bored)::

     % easy_install sphinx

5. **make sure** ``sphinx-build`` is in your path::

     % sphinx-build --help

6. **Install GNU Make**.  If you're on native Windows, to get a compatible
   GNU Make you should install the `MSYS Base System
   <http://sourceforge.net/projects/mingw/files/MSYS%20Base%20System/>`_.
   At the time of this writing, the latest with an executable
   installer is `version 1.0.11
   <http://sourceforge.net/projects/mingw/files/MSYS%20Base%20System/msys-1.0.11/MSYS-1.0.11.exe/download>`_.
   Make sure your PATH includes the path to the `make` executable::

     % make -v

   .. Note:: if you're on native windows (or MSYS) and the output ends with the line::

        This program built for i686-pc-cygwin

     or::

        This program built for i386-pc-mingw32

   Then you've done something wrong.  The platform string should be ``i386-pc-msys``.

7. **Install** GraphViz_.  Use your native package manager or get it
   from the GraphViz `download page <http://graphviz.org/Download.php>`_

8. **Install** Git_.  On Windows, this means MSysGit_.

.. _Git: http://git-scm.com
.. _MSysGit: http://code.google.com/p/msysgit/


Running the Build
=================

Now the easy part.  To *finally build* the documentation, enter the
``doc/`` subdirectory and issue the command::

  $ make html

The results will be generated in the ``build/html/`` subdirectory of
this project.  If you don't like building in your source tree, you can
change the parent of the generated ``html/`` directory by setting the
make (or environment) variable ``BUILDDIR``::

  $ make BUILDDIR=/tmp/ryppl-build html

.. _Python: http://python.org
.. _Sphinx: http://sphinx.pocoo.org/
.. _GNU Make: http://www.gnu.org/software/make/
.. _GraphViz: http://graphviz.org


................
Additional Notes
................

For more developer notes, please see the `Ryppl Wiki
<http://wiki.github.com/ryppl/ryppl/>`_.

.. [#upstream] Ian Bicking, the main developer of PIP, has signaled his
   intention to integrate our changes.
