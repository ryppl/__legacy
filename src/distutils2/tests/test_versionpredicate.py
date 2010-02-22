"""Tests harness for distutils2.versionpredicate.

"""

import distutils2.versionpredicate
import doctest

def test_suite():
    return doctest.DocTestSuite(distutils2.versionpredicate)
