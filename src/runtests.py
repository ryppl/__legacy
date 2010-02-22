"""Tests for distutils.

The tests for distutils2 are defined in the distutils2.tests package;
"""

import distutils2.tests
import test.test_support


def test_main():
    test.test_support.run_unittest(distutils2.tests.test_suite())
    test.test_support.reap_children()


if __name__ == "__main__":
    test_main()
