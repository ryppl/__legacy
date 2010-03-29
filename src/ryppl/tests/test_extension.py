"""Tests for distutils.extension."""
import unittest2
import os
import warnings

from distutils2.extension import Extension

class ExtensionTestCase(unittest2.TestCase):

    pass

def test_suite():
    return unittest2.makeSuite(ExtensionTestCase)

if __name__ == "__main__":
    unittest2.main(defaultTest="test_suite")
