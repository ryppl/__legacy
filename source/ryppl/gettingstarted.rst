.. highlight:: git_shell

.. _getting_started:

Getting started
---------------

Clone the superproject
^^^^^^^^^^^^^^^^^^^^^^

::

  git clone git://gitorious.org/ryppl/ryppl.git src

This will clone the ryppl *superproject* down to directory ``src``.
Have a look at the contents.  Most of boost is there, but:

* There is no toplevel ``boost`` directory, where one normally finds
  boosts' header files.

* There is a toplevel directory ``include``... but it is empty.

* Under ``libs``, there are empty subdirectories ``wave``,
  ``process``, ``chrono`` and ``fiber``. ::

    % ls -l libs/wave libs/chrono libs/process libs/fiber
    libs/chrono:
    total 0
    
    libs/fiber:
    total 0
    
    libs/process:
    total 0
    
    libs/wave:
    total 0
    
* Other than those four, each project (each one directory) under
  ``libs/`` contains a directory ``include/boost`` inside which are
  headers specific to this project, e.g. for *smart_ptr*::

    % ls libs/smart_ptr/include/boost 
    enable_shared_from_this.hpp
    make_shared.hpp scoped_array.hpp scoped_ptr.hpp shared_array.hpp
    shared_ptr.hpp smart_ptr/ smart_ptr.hpp

  Note that headers are not required to have any particular layout

* In the toplevel there is a file ``.gitmodules`` that maps local
  directories to remote git repositories::

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
    
* The command ``git submodule status`` gives the commits at which each
  submodule should be cloned::

    % git submodule status
    -6d205b973e41c226eba838ef125d5a14f508e173 libs/chrono
    -413d393f7aaea99c85d8db7bd93e06b99465e84c libs/fiber
    -d0698203f19bf30518f58ce8058dca496dba8ecf libs/process
    -f1e2aa9ad7743beaf11296e4f7d6f960814a86b7 libs/wave

Initialize and update the submodules
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Issue the command ``git submodule init``::

  % git submodule init
  Submodule 'libs/chrono' (git://gitorious.org/ryppl/chrono.git) registered for path 'libs/chrono'
  Submodule 'libs/fiber' (git://gitorious.org/ryppl/fiber.git) registered for path 'libs/fiber'
  Submodule 'libs/process' (git://gitorious.org/ryppl/process.git) registered for path 'libs/process'
  Submodule 'libs/wave' (git://gitorious.org/ryppl/wave.git) registered for path 'libs/wave'

Notice that the *submodule status* has not changed::

  % git submodule status
  -6d205b973e41c226eba838ef125d5a14f508e173 libs/chrono
  -413d393f7aaea99c85d8db7bd93e06b99465e84c libs/fiber
  -d0698203f19bf30518f58ce8058dca496dba8ecf libs/process
  -f1e2aa9ad7743beaf11296e4f7d6f960814a86b7 libs/wave

Now update the submodules::

  % git submodule update
  Initialized empty Git repository in /tmp/src/libs/chrono/.git/
  remote: Counting objects: 65, done.
  remote: Compressing objects: 100% (56/56), done.
  remote: Total 65 (delta 16), reused 0 (delta 0)
  Receiving objects: 100% (65/65), 79.53 KiB, done.
  Resolving deltas: 100% (16/16), done.
  Submodule path 'libs/chrono': checked out '6d205b973e41c226eba838ef125d5a14f508e173'
  Initialized empty Git repository in /tmp/src/libs/fiber/.git/
  remote: Counting objects: 103, done.
  remote: Compressing objects: 100% (100/100), done.
  remote: Total 103 (delta 34), reused 0 (delta 0)
  Receiving objects: 100% (103/103), 61.92 KiB, done.
  Resolving deltas: 100% (34/34), done.
  Submodule path 'libs/fiber': checked out '413d393f7aaea99c85d8db7bd93e06b99465e84c'
  Initialized empty Git repository in /tmp/src/libs/process/.git/
  remote: Counting objects: 128, done.
  Receiving objects: 100% (128/128), 100.10 KiB, done.g objects:  93% (120/128)   
  Resolving deltas: 100% (40/40), done.g deltas:   0% (0/40)   
  remote: Compressing objects: 100% (87/87), done.
  remote: Total 128 (delta 40), reused 120 (delta 38)
  Submodule path 'libs/process': checked out 'd0698203f19bf30518f58ce8058dca496dba8ecf'
  Initialized empty Git repository in /tmp/src/libs/wave/.git/
  remote: Counting objects: 469, done.
  remote: Compressing objects: 100% (222/222), done.
  remote: Total 469 (delta 233), reused 469 (delta 233)
  Receiving objects: 100% (469/469), 530.36 KiB | 256 KiB/s, done.
  Resolving deltas: 100% (233/233), done.
  Submodule path 'libs/wave': checked out 'f1e2aa9ad7743beaf11296e4f7d6f960814a86b7'
  
That's a lot of output... all that has happened is that a git checkout
of each submodule has been done to its corresponding directory inside
the superproject, and that the checkout has been done at a specific
commit.

Now notice that the git submodule status has changed::

  % git submodule status
  6d205b973e41c226eba838ef125d5a14f508e173 libs/chrono (heads/master)
  413d393f7aaea99c85d8db7bd93e06b99465e84c libs/fiber (heads/master)
  d0698203f19bf30518f58ce8058dca496dba8ecf libs/process (heads/master)
  f1e2aa9ad7743beaf11296e4f7d6f960814a86b7 libs/wave (heads/master)

The minus sign to the left of the hash has disappeared, and a branch
(in parenthesis) has appeared on the right.

Also, the submodule directories now contain code::

  % ls libs/process
  CMakeLists.txt  build/  example/  index.htm  test/
  README.txt      doc/    include/  source/
  
Now you have a **ryppl** workspace nearly ready to build.

Run cmake and generate forwarding headers
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Generate makefiles with *cmake* in the standard way.  I like to make a
subdirectory ``build/`` of my clone and run cmake in there, so that I
can always tell which build corresponds to which clone.  This
directory has already been added to ``.gitignore``, so git won't be
distracted by all those new buildfiles::

  % mkdir build
  % cd build
  % cmake ..
  -- The C compiler identification is GNU
  -- The CXX compiler identification is GNU

  [ etc ]

  -- 
  -- Reading boost project directories (per BUILD_PROJECTS) 
  -- 
  -- + preprocessor
  -- + concept_check

  [ etc... note that 'chrono', 'process', etc appear in this list ]

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

The last step is to generate forwarding headers.  This techinque is
borrowed from the smart guys at Trolltech ``Qt`` toolkit.  Make the
target **genheaders**::

  % make genheaders
  Scanning dependencies of target genheaders
  Generating central header directory
  Projects located under     :  /tmp/src/libs
  Fwding headers generated in:  /tmp/src/include

                serialization:  178
                    smart_ptr:  59
                 accumulators:  81

                     [etc etc]

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

  % make boost_fiber
  Scanning dependencies of target boost_fiber-mt-static-debug
  [  0%] Building CXX object libs/fiber/src/CMakeFiles/boost_fiber-mt-static-debug.dir/auto_reset_event.cpp.o
  [  0%] Building CXX object libs/fiber/src/CMakeFiles/boost_fiber-mt-static-debug.dir/condition.cpp.o

