
.. highlight:: git_shell

.. _getting_started:

Getting started
---------------

Boost is organized in Git as a “superproject” containing `submodules
<http://progit.org/book/ch6-6.html>`_, each of which corresponds to an
individual Boost library.  A **submodule** is a *reference* to a
commit in an *independent* Git repository.  The submodule is used by
Git to clone the independent repository below the superproject's root
directory, and check out the referenced commit.

Clone the Boost superproject
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

  git clone git://gitorious.org/ryppl/boost.git boost-ryppl

This will clone the rypplized boost *superproject* and place the
result in the top-level workspace directory ``boost-ryppl/``.  Have a look at
the contents.  Most of boost is there, but:

* In ``boost-ryppl/`` there is a file ``.gitmodules`` that maps local
  directories to remote git repositories::

    [submodule "src/accumulators"]
    	path = src/accumulators
    	url = git://gitorious.org/boost/accumulators.git
    [submodule "src/algorithm"]
    	path = src/algorithm
    	url = git://gitorious.org/boost/algorithm.git
    etc
    
* Under ``src`` there is an empty subdirectory for each boost library

* The command ``git submodule status`` gives the commits at which each
  submodule should be cloned:

.. parsed-literal::

    % git submodule status
    -10ac085df521b4b294afa074e296252fabd1735b src/accumulators
    -08578dcec8e5be7365e83107cae6f9240e215ed3 src/algorithm
    -d037b2069c9cce96f019b02a631a51a47970bc02 src/any
    -795ab423fecb41dba2e4e6a8be6ee8089d78136b src/array
    *etc…*

Initialize and update the submodules
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Issue the command ``git submodule init`` followed by ``git submodule update``:

.. parsed-literal::

  % git submodule init
  Submodule 'src/accumulators' (git://gitorious.org/boost/accumulators.git) registered for path 'src/accumulators'
  Submodule 'src/algorithm' (git://gitorious.org/boost/algorithm.git) registered for path 'src/algorithm'
  Submodule 'src/any' (git://gitorious.org/boost/any.git) registered for path 'src/any'
  Submodule 'src/array' (git://gitorious.org/boost/array.git) registered for path 'src/array'

  *etc…*

  % git submodule update
  Initialized empty Git repository in /tmp/boost-ryppl/cmake/.git/
  Submodule path 'cmake': checked out '6dce83c277d48644fac187799876799eb66c97a2'

  *etc…*

  
There will be alot of output...  Git has checked out each submodule to
its corresponding directory inside the superproject, and.

.. “that” above makes the sentence grammatically confusing.

Now notice that the git submodule status now *has* changed::

  % git submodule status
  6dce83c277d48644fac187799876799eb66c97a2 cmake (heads/master)
  0628a7a2d999bbbd62fd9877922c057f5f056114 src/accumulators (remotes/origin/1.41.0)
  5cec8044c5408fadee71110194027b0e99b44721 src/algorithm (remotes/origin/1.41.0)
  d58030ef644dc992db31fc2bd6fe3a985468eb4b src/any (remotes/origin/1.41.0)
  
The minus sign to the left of the hash has disappeared, and a branch
(in parenthesis) has appeared on the right.

Also, the submodule directories now contain code::

  % ls src/regex
  CMakeLists.txt	example/	module.cmake	src/
  build/		include/	performance/	test/
  doc/		index.html	README.txt	tools/

Now you have a Boost workspace nearly ready to build.

Run cmake and generate forwarding headers
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Create a build directory outside your source tree and run CMake there.
This step inspects your system configuration, finding installed
libraries, tools, etc., and generates appropriate makefiles for Boost:

.. parsed-literal::

  % mkdir ../build-ryppl
  % cd ../build-ryppl
  % cmake ../boost-ryppl
  -- The C compiler identification is GNU
  -- The CXX compiler identification is GNU

  *[ etc ]*

  -- 
  -- Reading boost project directories (per BUILD_PROJECTS) 
  -- 
  -- + preprocessor
  -- + concept_check

  *[ etc… note that 'chrono', 'process', etc appear in this list ]*

  -- + wave
  -- 
  -- BUILD_TESTS is NONE: skipping test directories. 
  -- 
  -- 
  -- BUILD_TOOLS is NONE: skipping tools. 
  -- 
  -- Configuring done
  -- Generating done
  -- Build files have been written to: *absolute-path-to-..*/build-ryppl

The last step is to generate forwarding headers.  This technique is
borrowed from the smart guys at Trolltech ``Qt`` toolkit.  Make the
target **genheaders**:

.. You need to explain where these headers go and what they do.

.. parsed-literal::

  % make genheaders
  Scanning dependencies of target genheaders
  Generating central header directory
  Projects located under     :  *absolute-path-to-..*/boost-ryppl
  Fwding headers generated in:  *absolute-path-to-..*/build-ryppl/include

                serialization:  178
                    smart_ptr:  59
                 accumulators:  81

                     *[etc etc]*

                   scope_exit:  1
                          mpl:  1041
                       assign:  16
  Built target genheaders


Now you'll notice that a  directory ``build-ryppl/include``
exists and is full of headers::

  % ls include/boost
  accumulators/                 multi_array/
  algorithm/                    multi_array.hpp
  aligned_storage.hpp           multi_index/

  [etc]

  memory_order.hpp              wave/
  mpi/                          wave.hpp
  mpi.hpp                       weak_ptr.hpp
  mpl/                          xpressive/

And that each file simply forwards to the project from whence it
came::

  % cat ../include/boost/wave.hpp 
  #include "../../src/wave/include/boost/wave.hpp"

Build
^^^^^

Now you can build.  To find the names of all available targets, make
the `help` target:

.. parsed-literal::

  % make help
  The following are some of the valid targets for this Makefile:
  ... all (the default if no target is provided)
  ... clean
  ... depend
  ... edit_cache
  ... genheaders
  ... install
  ... install/local
  ... install/strip
  ... list_install_components
  ... rebuild_cache
  ... test
  ... boost_date_time
  ... boost_date_time-mt-shared
  ... boost_date_time-mt-shared-debug
  ... boost_date_time-mt-static
  ... boost_date_time-mt-static-debug
  ... boost_thread
  *etc*

  % make boost_date_time
  [  0%] Built target boost_date_time-mt-static-debug
  [  0%] Built target boost_date_time-mt-shared-debug
  [  0%] Built target boost_date_time-mt-shared
  [100%] Built target boost_date_time-mt-static
  [100%] Built target boost_date_time
    

.. How do I test my library?
