.. boost-cmake documentation master file, created by
   sphinx-quickstart on Mon May 11 08:53:19 2009.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. _quickstart:

Quickstart
==========

This page describes how to configure and build Boost with CMake. By following these instructions, you should be able to get CMake, configure a Boost build tree to your liking with CMake, and then build, install, and package Boost libraries.

Download CMake
--------------

You can get it here:  http://www.cmake.org/HTML/Download.html

There are precompiled binaries for CMake on several different
platforms. The installation of these pre-compiled binaries is mostly
self-explanatory. If you need to build your own copy of CMake, please
see the `CMake installation instructions
<http://www.cmake.org/HTML/Install.html>`_.  In these instructions, we
will do things such that the Boost source tree (with CMake build
files) is available in the directory ``$BOOST/src`` and that the build
will happen in ``$BOOST/build``::

  $BOOST/
    src/     # (source checked out to here)
    build/   # (build output here) 

Note that it is *not* actually necessary to set any environment
variable ``BOOST``, this is a convention used in this document.
 
Check out the code
------------------

To get a copy of Boost with the CMake build system, retrieve it from
the Boost Subversion repository with the URL
`<http://svn.boost.org/svn/boost/branches/release>`_.

.. note:: The trunk is lagging behind the release (as we iterate
   	  towards the release of 1.40).  Please use the release
   	  branch, and let us know on the mailing list or IRC if you
   	  have problems.  *todo*: @1.40 time, remove this

On unix, ::

  mkdir $BOOST
  svn co http://svn.boost.org/svn/boost/branches/release $BOOST/src

Configure the Boost source tree
-------------------------------

This is the makefile generation step, using ``CMake``'s configuration tool. This step differs depending on whether you are using CMake's GUI on Microsoft Windows or whether you are using the command-line tools provided on Unix.

On Windows
^^^^^^^^^^

Run CMake by selecting it from the Start menu. 

      * Use the *Browse...* button to point CMake at the Boost source code in ``$BOOST\src``. 
      * Use the second *Browse...* button to select the directory where Boost will build binaries, ``$BOOST\build``. 
      * Click *Configure* a first time to configure Boost, which will search for various libraries on your system and prepare the build. 
      * CMake will ask you what kind of project files or make files to build. If you're using Microsoft Visual Studio, select the appropriate version to generate project files. Otherwise, you can use Borland's make files, generate NMake files, etc. 
      * You will then be given the opportunity to tune build options in the CMake GUI (see also [wiki:CMakeBuildConfiguration]. These options will affect what libraries are built and how.  They will initially appear red.  Click *Configure* again when you are done editing them.
      * Finally, click *OK* to generate project files.

On Unix
^^^^^^^

Create the directory that will hold the binaries that CMake build::

  mkdir $BOOST/build 

Change into the build directory you have just created::

  cd $BOOST/build 

Run the CMake configuration program, providing it with the Boost source directory::

  cmake $BOOST/src 

You'll see output from ``cmake``.  It looks somewhat like this::

  % cmake $BOOST/src 
  -- Check for working C compiler: /usr/bin/gcc
  -- Check for working C compiler: /usr/bin/gcc -- works
  -- Check size of void*
  -- Check size of void* - done
  -- Check for working CXX compiler: /usr/bin/c++
  -- Check for working CXX compiler: /usr/bin/c++ -- works
  -- Scanning subdirectories:
  --  + io
  --  + any
  --  + crc
  --  + mpl
  
    (etc, etc)
  
  --  + program_options
  --  + ptr_container
  --  + type_traits
  -- Configuring done
  -- Generating done
  -- Build files have been written to: $BOOST/build

The directory ``$BOOST/build`` should now contain a bunch of generated files, including a top level ``Makefile``, something like this::

  % ls
  CMakeCache.txt           CPackConfig.cmake    Makefile  
  cmake_install.cmake      libs/                CMakeFiles/     
  CPackSourceConfig.cmake  bin/                 lib/

That's it! You've now configured your source tree and are ready to start building Boost.

Build Boost
-----------

Like configuration, the way in which one builds Boost with CMake differs from one platform to another, depending on your platform and how you configured CMake. Either way, you'll be using the tools provided to you by your compiler or operating system vendor.

Microsoft Visual Studio
-----------------------

If you have generated project files for Microsoft Visual Studio, you
will need to start up Visual Studio to build Boost. Once Visual Studio
has loaded, load the solution or project``Boost`` from the Boost build
directory you set in the CMake configuration earlier. Then, just click
"Build" to build all of Boost.

On Unix (and when using makefile variants on Microsoft Windows)
---------------------------------------------------------------

One builds using standard "make" tools. In the directory $BOOST/build
(where the generated makefiles are) run ``make``:

  make

That's it! Once the build completes (which make take a while, if you
are building all of the Boost libraries), the Boost libraries will be
available in the ``lib`` subdirectory of your build directory, ready
to be used, installed, or packaged.

Installing Boost
----------------

The installation of Boost's headers and compiled libraries uses the
same tools as building the library. With Microsoft Visual Studio, just
load the Boost solution or project and build the 'INSTALL' target to
perform the installation. Unix and makefile users will change into the
Boost build directory and use the ``install`` make target, e.g.,

  make install

