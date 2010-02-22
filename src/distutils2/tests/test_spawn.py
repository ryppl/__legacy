"""Tests for distutils.spawn."""
import unittest2
import os
import time
from distutils2.tests import captured_stdout

from distutils2.spawn import _nt_quote_args
from distutils2.spawn import spawn, find_executable
from distutils2.errors import DistutilsExecError
from distutils2.tests import support

class SpawnTestCase(support.TempdirManager,
                    support.LoggingSilencer,
                    unittest2.TestCase):

    def test_nt_quote_args(self):

        for (args, wanted) in ((['with space', 'nospace'],
                                ['"with space"', 'nospace']),
                               (['nochange', 'nospace'],
                                ['nochange', 'nospace'])):
            res = _nt_quote_args(args)
            self.assertEquals(res, wanted)


    @unittest2.skipUnless(os.name in ('nt', 'posix'),
                         'Runs only under posix or nt')
    def test_spawn(self):
        tmpdir = self.mkdtemp()

        # creating something executable
        # through the shell that returns 1
        if os.name == 'posix':
            exe = os.path.join(tmpdir, 'foo.sh')
            self.write_file(exe, '#!/bin/sh\nexit 1')
            os.chmod(exe, 0777)
        else:
            exe = os.path.join(tmpdir, 'foo.bat')
            self.write_file(exe, 'exit 1')

        os.chmod(exe, 0777)
        self.assertRaises(DistutilsExecError, spawn, [exe])

        # now something that works
        if os.name == 'posix':
            exe = os.path.join(tmpdir, 'foo.sh')
            self.write_file(exe, '#!/bin/sh\nexit 0')
            os.chmod(exe, 0777)
        else:
            exe = os.path.join(tmpdir, 'foo.bat')
            self.write_file(exe, 'exit 0')

        os.chmod(exe, 0777)
        spawn([exe])  # should work without any error

def test_suite():
    return unittest2.makeSuite(SpawnTestCase)

if __name__ == "__main__":
    unittest2.main(defaultTest="test_suite")
