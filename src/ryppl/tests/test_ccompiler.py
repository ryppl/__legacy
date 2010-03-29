"""Tests for distutils.ccompiler."""
import os
import unittest2
from distutils2.tests import captured_stdout

from distutils2.compiler.ccompiler import (gen_lib_options, CCompiler,
                                 get_default_compiler, customize_compiler)
from distutils2.tests import support

class FakeCompiler(object):
    def library_dir_option(self, dir):
        return "-L" + dir

    def runtime_library_dir_option(self, dir):
        return ["-cool", "-R" + dir]

    def find_library_file(self, dirs, lib, debug=0):
        return 'found'

    def library_option(self, lib):
        return "-l" + lib

class CCompilerTestCase(support.EnvironGuard, unittest2.TestCase):

    def test_gen_lib_options(self):
        compiler = FakeCompiler()
        libdirs = ['lib1', 'lib2']
        runlibdirs = ['runlib1']
        libs = [os.path.join('dir', 'name'), 'name2']

        opts = gen_lib_options(compiler, libdirs, runlibdirs, libs)
        wanted = ['-Llib1', '-Llib2', '-cool', '-Rrunlib1', 'found',
                  '-lname2']
        self.assertEquals(opts, wanted)

    def test_customize_compiler(self):

        # not testing if default compiler is not unix
        if get_default_compiler() != 'unix':
            return

        os.environ['AR'] = 'my_ar'
        os.environ['ARFLAGS'] = '-arflags'

        # make sure AR gets caught
        class compiler:
            compiler_type = 'unix'

            def set_executables(self, **kw):
                self.exes = kw

        comp = compiler()
        customize_compiler(comp)
        self.assertEquals(comp.exes['archiver'], 'my_ar -arflags')

def test_suite():
    return unittest2.makeSuite(CCompilerTestCase)

if __name__ == "__main__":
    unittest2.main(defaultTest="test_suite")
