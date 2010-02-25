"""Tests for distutils.filelist."""
from os.path import join
import unittest2
from distutils2.tests import captured_stdout

from distutils2.filelist import glob_to_re, FileList

MANIFEST_IN = """\
include ok
include xo
exclude xo
include foo.tmp
global-include *.x
global-include *.txt
global-exclude *.tmp
recursive-include f *.oo
recursive-exclude global *.x
graft dir
prune dir3
"""

class FileListTestCase(unittest2.TestCase):

    # this only works on 2.7
    def _test_glob_to_re(self):
        # simple cases
        self.assertEquals(glob_to_re('foo*'), 'foo[^/]*\\Z(?ms)')
        self.assertEquals(glob_to_re('foo?'), 'foo[^/]\\Z(?ms)')
        self.assertEquals(glob_to_re('foo??'), 'foo[^/][^/]\\Z(?ms)')

        # special cases
        self.assertEquals(glob_to_re(r'foo\\*'), r'foo\\\\[^/]*\Z(?ms)')
        self.assertEquals(glob_to_re(r'foo\\\*'), r'foo\\\\\\[^/]*\Z(?ms)')
        self.assertEquals(glob_to_re('foo????'), r'foo[^/][^/][^/][^/]\Z(?ms)')
        self.assertEquals(glob_to_re(r'foo\\??'), r'foo\\\\[^/][^/]\Z(?ms)')

    def test_process_template_line(self):
        # testing  all MANIFEST.in template patterns
        file_list = FileList()

        # simulated file list
        file_list.allfiles = ['foo.tmp', 'ok', 'xo', 'four.txt',
                              join('global', 'one.txt'),
                              join('global', 'two.txt'),
                              join('global', 'files.x'),
                              join('global', 'here.tmp'),
                              join('f', 'o', 'f.oo'),
                              join('dir', 'graft-one'),
                              join('dir', 'dir2', 'graft2'),
                              join('dir3', 'ok'),
                              join('dir3', 'sub', 'ok.txt')
                              ]

        for line in MANIFEST_IN.split('\n'):
            if line.strip() == '':
                continue
            file_list.process_template_line(line)

        wanted = ['ok', 'four.txt', join('global', 'one.txt'),
                  join('global', 'two.txt'), join('f', 'o', 'f.oo'),
                  join('dir', 'graft-one'), join('dir', 'dir2', 'graft2')]

        self.assertEquals(file_list.files, wanted)

def test_suite():
    return unittest2.makeSuite(FileListTestCase)

if __name__ == "__main__":
    unittest2.main(defaultTest="test_suite")
