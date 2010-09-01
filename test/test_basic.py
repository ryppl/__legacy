import os,sys
from path import Path
from pkgtest import mktree
from urllib import pathname2url
from cStringIO import StringIO
from ryppl_test import Environment as new_test, create_projects
from testutil import mkdtemp, _temp_dirs, exe_ext as EXE

here = Path(__file__).abspath.folder
distutils2_src = here.folder/'submodule'/'distutils2'/'src'

try:
    import distutils2
except ImportError:
    sys.path.insert(0, distutils2_src)
    import distutils2

from distutils2.metadata import DistributionMetadata as METADATA

# This scripts gets found and run by nosetests because its name matches nosetests
# naming conventions. Also, the functions below of the form test_xxx() are found
# and executed as individual tests for the same reason. 
#
# Each test gets run in its own virtualenv. The creation of a new Environment
# object (by new_text()) causes the creation of the virtualenv. That causes the
# os.environ['PATH'] to be updated so that the virtualenv's python is the one
# that is found. Any external python scripts executed by launching a separate
# instance of python will use that virtualenv. For tnat invocation of python,
# the libs, site-packages and bin paths all point to that virtualenv. THAT MAKES
# IT BEHAVE DIFFERENTLY THEN THE CURRENT INVOCATION OF PYTHON WHICH IS IN A
# DIFFERENT VIRTUALENV.

def test_fetch():
    env = new_test()
    index,project_paths = create_projects(
        env, my_proj=open(distutils2_src/'distutils2'/'tests'/'PKG-INFO').read())
    env.ryppl('install', '--no-install', '-vvv', '-i', index, 'my_proj')

def test_diamond():
    env = new_test()
    index,projects = create_projects(
        env,
        ProjA=dict(requires_dist=['ProjB','ProjC']),
        ProjB=dict(requires_dist=['ProjD<1.0']),
        ProjC=dict(requires_dist=['ProjD>1.0']),
        ProjD=dict(),
        )

    d = projects['ProjD'].path
    env.run('git', 'tag', '0.9', cwd=d)
    open(d/'later','w').write('update project')
    env.run('git', 'add', 'later', cwd=d)
    env.run('git', 'commit', '-m', 'update', cwd=d)
    env.run('git', 'tag', '1.1', cwd=d)
    env.ryppl('install', 
          # '--no-install', 
          '-vvv', '-i', index, 'ProjA')

# Test that a project with a CMakeLists.txt gets built and installed correctly
# by ryppl
def test_cmake():
    env = new_test()
    index,projects = create_projects(
        env,
        greet=dict())

    greet = projects['greet']
    greet.add_file('CMakeLists.txt', '''
cmake_minimum_required(VERSION 2.8)
project (greet)
add_executable(greet hello.cpp)
install (TARGETS greet 
  RUNTIME DESTINATION ${CMAKE_INSTALL_PREFIX}
)
''')

    greet.add_file('hello.cpp', '''
#include <iostream>
int main() {
    std::cout << "hello ryppl\\n";
}
''')
    env.ryppl('install', '-vvv', '-i', index, 'greet')
    result = env.run('greet')
    if not result.stdout == 'hello ryppl\n':
        raise AssertionError(
            'Unexpected output from greet executable. Expected "%s", got "%s"'
                % ('hello ryppl\\n', result.stdout))

# Test that a CMake project can be installed and uninstalled correctly by ryppl
def test_uninstall():
    env = new_test()
    index,projects = create_projects(
        env,
        empty=dict())

    empty = projects['empty']
    empty.add_file('CMakeLists.txt', '''
cmake_minimum_required(VERSION 2.8)
project (empty)
add_executable(empty empty.cpp)
install (TARGETS empty 
  RUNTIME DESTINATION ${CMAKE_INSTALL_PREFIX}
)
''')

    empty.add_file('empty.cpp', 'int main() {\n}\n')

    # create a temporary path. We'll install the exe here.
    runtime_dst = Path(env.bin_path)/'empty-bin'
    install_option = '--install-option=--install-scripts='+runtime_dst

    # install the package and confirm that the file exists
    # in the place we expect it to
    env.ryppl('install', '-vvv', install_option, '-i', index, 'empty')
    if not os.path.isfile(runtime_dst/('empty'+EXE)):
        raise AssertionError(
            'Failed to find installed file at "%s"' % (runtime_dst/('empty'+EXE)))

    # uninstall the packageand confirm the file as been deleted
    env.ryppl('uninstall', '-vvv', '-y', 'empty')
    if os.path.isfile(runtime_dst/('empty'+EXE)):
        raise AssertionError(
            'Failed to uninstall file at "%s"' % (runtime_dst/('empty'+EXE)))


# Test that two cmake projects, one which depends on the other, both get
# downloaded, built and installed correctly
def test_library():
    env = new_test()
    index,projects = create_projects(
        env,
        greetexe=dict(requires_dist=['greetlib']),
        greetlib=dict())

    greetexe = projects['greetexe']
    greetexe.add_file('CMakeLists.txt', '''
cmake_minimum_required(VERSION 2.8)
project (greetexe)
add_executable(greetexe hello.cpp)
find_library (GREETLIB_LIBRARY NAMES greetlib)
if (GREETLIB_LIBRARY)
    MESSAGE(STATUS "Found greetlib: ${GREETLIB_LIBRARY}")
else (GREETLIB_LIBRARY)
    MESSAGE(FATAL_ERROR "Could not find greetlib")
endif (GREETLIB_LIBRARY)
include_directories ("${CMAKE_INSTALL_PREFIX}/include")
target_link_libraries (greetexe "${GREETLIB_LIBRARY}")
install (TARGETS greetexe DESTINATION "${CMAKE_INSTALL_PREFIX}")
''')

    greetexe.add_file('hello.cpp', '''
#include "projB/hello.hpp"
int main() {
    greet();
}
''')

    greetlib = projects['greetlib']
    greetlib.add_file('CMakeLists.txt', '''
cmake_minimum_required(VERSION 2.8)
add_library(greetlib hello.cpp)
install (TARGETS greetlib DESTINATION "${CMAKE_INSTALL_PREFIX}")
install (FILES hello.hpp DESTINATION "${CMAKE_INSTALL_PREFIX}/include/projB")
''')

    greetlib.add_file('hello.cpp', '''
#include "./hello.hpp"
#include <iostream>
void greet() {
    std::cout << "hello ryppl\\n";
}
''')

    greetlib.add_file('hello.hpp', '''
#ifndef GREET_HPP
#define GREET_HPP
void greet();
#endif
''')

    # BUGBUG pip doesn't have a notion of build/install
    # dependencies, so we have to be explicit about installing
    # the lib before the exe. MUST FIX UPSTREAM IF POSSIBLE.
    env.ryppl('install', '-vvv', '-i', index, 'greetlib')
    env.ryppl('install', '-vvv', '-i', index, 'greetexe')
    result = env.run('greetexe')
    if not result.stdout == 'hello ryppl\n':
        raise AssertionError(
            'Unexpected output from greetexe executable. Expected "%s", got "%s"'
                % ('hello ryppl\\n', result.stdout))

if __name__ == '__main__':
    test_fetch()
    test_diamond()
    test_cmake()
    test_uninstall()
    test_library()

