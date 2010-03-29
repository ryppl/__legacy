"""Tests for distutils2.core."""

import StringIO
import distutils2.core
import os
import shutil
import sys
from distutils2.tests import captured_stdout
import unittest2
from distutils2.tests import support

# setup script that uses __file__
setup_using___file__ = """\

__file__

from distutils2.core import setup
setup()
"""

setup_prints_cwd = """\

import os
print os.getcwd()

from distutils2.core import setup
setup()
"""


class CoreTestCase(support.EnvironGuard, unittest2.TestCase):

    def setUp(self):
        super(CoreTestCase, self).setUp()
        self.old_stdout = sys.stdout
        self.cleanup_testfn()
        self.old_argv = sys.argv, sys.argv[:]

    def tearDown(self):
        sys.stdout = self.old_stdout
        self.cleanup_testfn()
        sys.argv = self.old_argv[0]
        sys.argv[:] = self.old_argv[1]
        super(CoreTestCase, self).tearDown()

    def cleanup_testfn(self):
        path = distutils2.tests.TESTFN
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)

    def write_setup(self, text, path=distutils2.tests.TESTFN):
        open(path, "w").write(text)
        return path

    def test_run_setup_provides_file(self):
        # Make sure the script can use __file__; if that's missing, the test
        # setup.py script will raise NameError.
        distutils2.core.run_setup(
            self.write_setup(setup_using___file__))

    def test_run_setup_uses_current_dir(self):
        # This tests that the setup script is run with the current directory
        # as its own current directory; this was temporarily broken by a
        # previous patch when TESTFN did not use the current directory.
        sys.stdout = StringIO.StringIO()
        cwd = os.getcwd()

        # Create a directory and write the setup.py file there:
        os.mkdir(distutils2.tests.TESTFN)
        setup_py = os.path.join(distutils2.tests.TESTFN, "setup.py")
        distutils2.core.run_setup(
            self.write_setup(setup_prints_cwd, path=setup_py))

        output = sys.stdout.getvalue()
        if output.endswith("\n"):
            output = output[:-1]
        self.assertEqual(cwd, output)

def test_suite():
    return unittest2.makeSuite(CoreTestCase)

if __name__ == "__main__":
    unittest2.main(defaultTest="test_suite")
