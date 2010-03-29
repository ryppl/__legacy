"""Test suite for ryppl.

This test suite consists of a collection of test modules in the
ryppl.tests package.  Each test module has a name starting with
'test' and contains a function test_suite().  The function is expected
to return an initialized unittest2.TestSuite instance.

Tests for the command classes in the ryppl.command package are
included in ryppl.tests as well, instead of using a separate
ryppl.command.tests package, since command identification is done
by import rather than matching pre-defined names.

"""
from distutils2.tests import *

from test.test_support import TESTFN    # use TESTFN from stdlib/test_support.

here = os.path.dirname(__file__)

verbose = 1


def test_suite():
    suite = unittest2.TestSuite()
    for fn in os.listdir(here):
        if fn.startswith("test") and fn.endswith(".py"):
            modname = "ryppl.tests." + fn[:-3]
            __import__(modname)
            module = sys.modules[modname]
            suite.addTest(module.test_suite())
    return suite

if __name__ == "__main__":
    unittest2.main(defaultTest="test_suite")
