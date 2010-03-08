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

  git clone git://gitorious.org/ryppl/boost.git src

This will clone the rypplized boost *superproject* and place the
result in the top-level workspace directory ``src/``.  Have a look at
the contents.  Most of boost is there, but:

.. Using “src” here doesn't feel right; too generic.  Maybe “boost-src?”

* There is no toplevel ``boost`` directory, where one normally finds
  boosts' header files.

* There is a toplevel directory ``include``... but it is empty.

* Under ``libs``, all subdirectories are empty.

* In the ``src`` there is a file ``.gitmodules`` that maps local
  directories to remote git repositories::

    [submodule "libs/accumulators"]
    	path = libs/accumulators
    	url = git://gitorious.org/boost/accumulators.git
    [submodule "libs/algorithm"]
    	path = libs/algorithm
    	url = git://gitorious.org/boost/algorithm.git
    etc
    
* The command ``git submodule status`` gives the commits at which each
  submodule should be cloned:

.. parsed-literal::

    % git submodule status
    -10ac085df521b4b294afa074e296252fabd1735b libs/accumulators
    -08578dcec8e5be7365e83107cae6f9240e215ed3 libs/algorithm
    -d037b2069c9cce96f019b02a631a51a47970bc02 libs/any
    -795ab423fecb41dba2e4e6a8be6ee8089d78136b libs/array
    *etc…*

Initialize and update the submodules
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Issue the command ``git submodule init``::

  % git submodule init
  Submodule 'libs/accumulators' (git://gitorious.org/boost/accumulators.git) registered for path 'libs/accumulators'
  Submodule 'libs/algorithm' (git://gitorious.org/boost/algorithm.git) registered for path 'libs/algorithm'
  Submodule 'libs/any' (git://gitorious.org/boost/any.git) registered for path 'libs/any'
  Submodule 'libs/array' (git://gitorious.org/boost/array.git) registered for path 'libs/array'
  [etc]  

Notice at this point that the *submodule status* has not changed.Now
update the submodules:

.. Why does the reader care that the submodule status hasn't changed?
.. I don't think we want to be teaching Git in this document, do you?
.. Why don't we just do “git submodule update --init”?

::

  % git submodule update
  Initialized empty Git repository in /tmp/boost/cmake/.git/
  remote: Counting objects: 263, done.
  [etc]
  
There will be alot of output...  a git checkout of each submodule has
been done to its corresponding directory inside the superproject, and
that the checkout has been done at a specific commit.

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

  % ls libs/process
  CMakeLists.txt  build/  example/  index.htm  test/
  README.txt      doc/    include/  source/
  
Now you have a Boost workspace nearly ready to build.

.. Used to say “ryppl workspace.”  I think that's confusing, implying
.. this procedure is more generic than it actually is.  A project with
.. no ryppl dependencies might not need any submodules, for example.

Run cmake and generate forwarding headers
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Generate makefiles with *cmake* in the standard way.  
.. I think we should say “configure with cmake” instead.  This does
.. more than simply generating makefiles, right?
I like to make a
subdirectory ``build/`` of my workspace and run cmake in there, so
that I can always tell which build corresponds to which workspace.
.. That is confusingly phrased: 1. The reader has no concept of why
.. there might be multiple workspaces 2. What happens if I run cmake
.. without the subdirectory?  Don't I still get build results
.. associated with the workspace?  This path has already been added to
``.gitignore``, so all those new buildfiles won't look to git like
they need to be added to the project:

.. parsed-literal::

  % mkdir build
  % cd build
  % cmake ..
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
  -- Build files have been written to: /tmp/src/build

The last step is to generate forwarding headers.  This technique is
borrowed from the smart guys at Trolltech ``Qt`` toolkit.  Make the
target **genheaders**:

.. You need to explain where these headers go and what they do.

.. parsed-literal::

  % make genheaders
  Scanning dependencies of target genheaders
  Generating central header directory
  Projects located under     :  /tmp/src/libs
  Fwding headers generated in:  /tmp/src/include

                serialization:  178
                    smart_ptr:  59
                 accumulators:  81

                     *[etc etc]*

                   scope_exit:  1
                          mpl:  1041
                       assign:  16
  Built target genheaders

Now you'll notice that a superproject directory ``include/boost``
exists and is full of headers::

  % ls ../include/boost
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
  #include "../../libs/wave/include/boost/wave.hpp"

Note also that the presence of generated files in ``build/`` and
``include/`` don't worry git::

  % git status
  # On branch master
  nothing to commit (working directory clean)

Thanks to the file ``.gitignore``.

Build
^^^^^

Now you can build::

  % make boost_system
  Scanning dependencies of target boost_system-mt-static-debug
  Building CXX object src/system/src/CMakeFiles/boost_system-mt-static-debug.dir/error_code.cpp.o
  Linking CXX static library ../../../lib/libboost_system-mt-d.a
  Built target boost_system-mt-static-debug
  

.. How do I test my library?
