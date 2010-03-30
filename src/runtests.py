"""Tests for ryppl.

The tests for ryppl are defined in the ryppl.tests package;
"""

import ryppl.tests
from ryppl.tests import run_unittest, reap_children

def test_main():
    run_unittest(ryppl.tests.test_suite())
    reap_children()


if __name__ == "__main__":
    test_main()
