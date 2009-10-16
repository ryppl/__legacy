Notes by Boost Version
======================

.. warning:: -DCMAKE_IS_EXPERIMENTAL=ORLY_YARLY

   This guard variable is included in releases of Boost.CMake through
   version 1.38.  You just need to set this variable to some value (be
   creative) when running cmake for the first time to disable the
   guard.

1.35.0 - 1.37
-------------

There was a CMake branch that built these releases, but Boost.CMake
was not included in the official distribution.

1.38.0 and 1.39.0
-----------------

Boost.CMake was included as an experimental system for the first time.
It is perfectly capable of doing the basic build and install of boost.
You *must* pass the argument ::

  -DCMAKE_IS_EXPERIMENTAL=ORLY

to the initial run of cmake, or you will see an intimidating message
explaining that Boost.CMake != Boost.Build.  It looks like this::

  -- ##########################################################################
  -- 
  --               Only Boost.Build is officially supported.
  -- 
  --                       This is not Boost.Build.
  -- 
  --  This is an alternate, cmake-based build system that is currently under development.
  --  To try it out, invoke CMake with the argument
  --         -DCMAKE_IS_EXPERIMENTAL=YES_I_KNOW
  --  Or use the gui to set the variable CMAKE_IS_EXPERIMENTAL to some value.
  --  This will only be necessary the first time.
  --  
  --  For more information on boost-cmake see the wiki:
  --      https://svn.boost.org/trac/boost/wiki/CMake
  -- 
  --  Subscribe to the mailing list:
  --      http://lists.boost.org/mailman/listinfo.cgi/boost-cmake
  -- 
  --  NOTE:  Please ask questions about this build system on the boost-cmake list,
  --         not on other boost lists.
  -- 
  --  And/or check the archives:
  --      http://news.gmane.org/gmane.comp.lib.boost.cmake
  -- 
  -- ##########################################################################
  CMake Error at CMakeLists.txt:61 (message):
    Magic variable CMAKE_IS_EXPERIMENTAL unset.
  
  
  -- Configuring incomplete, errors occurred!

Again, f you see this, just set that guard variable to something, to
demonstrate your tenacity and dedication.  Then things will work fine.

.. rubric:: Quick and dirty HOWTO

::

  % mkdir /tmp/boost
  % cd /tmp/boost
  % svn co https://svn.boost.org/svn/boost/tags/release/Boost_1_38_0 src
  % mkdir build
  % cd build
  % cmake -DCMAKE_IS_EXPERIMENTAL=ORLY -DCMAKE_INSTALL_PREFIX=/path/to/installdir ../src

At this point, you have two options: you either want to leave boost in
place and use it there, or you want to install it to a particular
location.  

**In-place**

  If you're competent to specify header/library paths
  yourself and want to build in place::
  
    % make
  
  and your libraries will be in /tmp/boost/build/lib, and the headers in
  /tmp/boost/src, (where you'd expect them to be).
  
**Installed to some location**

  This will install boost to ``lib/`` and ``include/`` under the
  ``CMAKE_INSTALL_PREFIX`` given above::
  
    % make modularize   # shuffles some headers around
    % make install

.. warning:: 

   In versions 1.38 and 1.39, if you want to ``make install``, you
   *must* ``make modularize`` first.  This is an intermediate step
   that we expect to go away in future versions.

Also note that cmake supports ``DESTDIR`` for making .deb and .rpm
packages;  see the standard cmake documentation 

Known Issues
^^^^^^^^^^^^

* There isn't much support for building/running tests within boost in
  these releases.
* In version 1.39, the ``BOOST_VERSION_MINOR`` is wrong: it is set to
  1.38.  You can set this manually by looking for
  ``BOOST_VERSION_MINOR`` in the toplevel ``CMakeLists.txt``
* The boost build names the ``boost_prg_exec_monitor`` and
  ``boost_unit_test_framework`` libraries with an additional trailing
  ``-s``.  You will probably need to modify your build if you use
  these libraries.
