"""Tests for distutils.archive_util."""
__revision__ = "$Id: test_archive_util.py 75659 2009-10-24 13:29:44Z tarek.ziade $"

import unittest
import warnings
from distutils.archive_util import (check_archive_formats, make_archive,
                                    make_tarball, make_zipfile)
from test.test_support import check_warnings

class ArchiveUtilTestCase(unittest.TestCase):

    def test_warnings(self):
        # other tests were moved in test_shutil, but let's make sure a warning
        # is popped if the old api is used
        with check_warnings() as w:
            warnings.simplefilter("always")

            # doing various "valid" calls to trigger warnings
            self.assertEquals(check_archive_formats(['gztar', 'xxx', 'zip']),
                              'xxx')
            self.assertEquals(check_archive_formats(['gztar', 'zip']), None)

            try:
                make_archive('xx', 'xx')
            except ValueError:
                pass

            try:
                make_tarball('IDONTEXIST', 'IDONTEXIST')
            except Exception:
                pass

            try:
                make_zipfile('IDONTEXIST', 'IDONTEXIST')
            except Exception:
                pass

        self.assertEquals(len(w.warnings), 5)


def test_suite():
    return unittest.makeSuite(ArchiveUtilTestCase)

if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")
