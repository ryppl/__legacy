"""Test suite for distutils.

This test suite consists of a collection of test modules in the
distutils.tests package.  Each test module has a name starting with
'test' and contains a function test_suite().  The function is expected
to return an initialized unittest2.TestSuite instance.

Tests for the command classes in the distutils.command package are
included in distutils.tests as well, instead of using a separate
distutils.command.tests package, since command identification is done
by import rather than matching pre-defined names.

"""
import os
import sys
import warnings
import unittest2

from test.test_support import TESTFN    # use TESTFN from stdlib/test_support.

here = os.path.dirname(__file__)

verbose = 1


def test_suite():
    suite = unittest2.TestSuite()
    for fn in os.listdir(here):
        if fn.startswith("test") and fn.endswith(".py"):
            modname = "distutils2.tests." + fn[:-3]
            __import__(modname)
            module = sys.modules[modname]
            suite.addTest(module.test_suite())
    return suite

class Error(Exception):
    """Base class for regression test exceptions."""


class TestFailed(Error):
    """Test failed."""


class BasicTestRunner:
    def run(self, test):
        result = unittest2.TestResult()
        test(result)
        return result


def _run_suite(suite):
    """Run tests from a unittest2.TestSuite-derived class."""
    if verbose:
        runner = unittest2.TextTestRunner(sys.stdout, verbosity=2)
    else:
        runner = BasicTestRunner()

    result = runner.run(suite)
    if not result.wasSuccessful():
        if len(result.errors) == 1 and not result.failures:
            err = result.errors[0][1]
        elif len(result.failures) == 1 and not result.errors:
            err = result.failures[0][1]
        else:
            err = "errors occurred; run in verbose mode for details"
        raise TestFailed(err)


def run_unittest(*classes):
    """Run tests from unittest2.TestCase-derived classes.

    Extracted from stdlib test.test_support and modified to support unittest2.
    """
    valid_types = (unittest2.TestSuite, unittest2.TestCase)
    suite = unittest2.TestSuite()
    for cls in classes:
        if isinstance(cls, str):
            if cls in sys.modules:
                suite.addTest(unittest2.findTestCases(sys.modules[cls]))
            else:
                raise ValueError("str arguments must be keys in sys.modules")
        elif isinstance(cls, valid_types):
            suite.addTest(cls)
        else:
            suite.addTest(unittest2.makeSuite(cls))
    _run_suite(suite)


def reap_children():
    """Use this function at the end of test_main() whenever sub-processes
    are started.  This will help ensure that no extra children (zombies)
    stick around to hog resources and create problems when looking
    for refleaks.

    Extracted from stdlib test.test_support.
    """

    # Reap all our dead child processes so we don't leave zombies around.
    # These hog resources and might be causing some of the buildbots to die.
    if hasattr(os, 'waitpid'):
        any_process = -1
        while True:
            try:
                # This will raise an exception on Windows.  That's ok.
                pid, status = os.waitpid(any_process, os.WNOHANG)
                if pid == 0:
                    break
            except:
                break

def captured_stdout(func, *args, **kw):
    import StringIO
    orig_stdout = getattr(sys, 'stdout')
    setattr(sys, 'stdout', StringIO.StringIO())
    try:
        res = func(*args, **kw)
        sys.stdout.seek(0)
        return res, sys.stdout.read()
    finally:
        setattr(sys, 'stdout', orig_stdout)

def unload(name):
    try:
        del sys.modules[name]
    except KeyError:
        pass


if __name__ == "__main__":
    unittest2.main(defaultTest="test_suite")
