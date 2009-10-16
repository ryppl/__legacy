.. index:: boost_library_project

boost_library_project
---------------------

Define a boost library project.

.. cmake:: boost_library_project(libname[, ...])

   :param libname: name of library to add
   :type SRCDIRS: optional
   :param SRCDIRS: srcdir1 srcdir2 ...
   :type TESTDIRS: optional
   :param TESTDIRS: testdir1 testdir2 ..
   :param DESCRIPTION: description
   :param AUTHORS: author1 author2
   :param MAINTAINERS: maint maint2
   :type MODULAR: optional 
   :param MODULAR:

where `libname` is the name of the library (e.g., Python,
Filesystem), `srcdir1`, `srcdir2`, etc, are subdirectories containing
library sources (for Boost libraries that build actual library
binaries), and `testdir1`, `testdir2`, etc, are subdirectories
containing regression tests.

A library marked MODULAR has all of its header files in its own
subdirectory include/boost rather than the "global" boost
subdirectory. These libraries can be added or removed from the tree
freely; they do not need to be a part of the main repository.
 
`DESCRIPTION` provides a brief description of the library, which can
be used to summarize the behavior of the library for a user. `AUTHORS`
lists the authors of the library, while `MAINTAINERS` lists the active
maintainers. If `MAINTAINERS` is left empty, it is assumed that the 
authors are still maintaining the library. Both authors and maintainers
should have their name followed by their current e-mail address in
angle brackets, with -at- instead of the at sign, e.g., ::

  Douglas Gregor <doug.gregor -at- gmail.com>

For libraries that build actual library binaries, this macro adds a
option `BUILD_BOOST_LIBNAME` (which defaults to ON). When the option
is ON, this macro will include the source subdirectories, and
therefore, will build and install the library binary.

For libraries that have regression tests, and when testing is
enabled globally by the `BUILD_REGRESSION_TESTS` option, this macro also
defines the `TEST_BOOST_LIBNAME` option (defaults to ON). When ON, the
generated makefiles/project files will contain regression tests for
this library.
   
.. rubric:: Example

The Boost.Thread library uses the following invocation of the
`boost_library_project` macro, since it has both a compiled library
(built in the "src" subdirectory) and regression tests (listed in the
"test" subdirectory)::


  boost_library_project(
    Thread
    SRCDIRS src 
    TESTDIRS test 
    DESCRIPTION "Portable threading"
    AUTHORS "Anthony Williams <anthony -at- justsoftwaresolutions.co.uk">
    )

.. rubric:: Where Defined

This macro is defined in the Boost Core module in
``tools/build/CMake/BoostCore.cmake``

