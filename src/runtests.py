"""Tests for distutils2.

The tests for distutils2 are defined in the distutils2.tests package;
"""

import distutils2.tests
from distutils2.tests import run_unittest, reap_children

from distutils2._backport.tests import test_suite as btest_suite

def test_main():
    run_unittest(distutils2.tests.test_suite())
    run_unittest(btest_suite())
    reap_children()


if __name__ == "__main__":
    test_main()
